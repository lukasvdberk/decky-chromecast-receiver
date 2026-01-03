import os
import decky
import asyncio
from pathlib import Path

# plugin related
PLUGIN_NAME="decky-chromecast-receiver"

# player cast related
PLAYER_CAST_NAME="steam-deck"
PLAYER_CAST_PLAYER="mpv" # default by playercast themselves
PLAYER_CAST_BIN = "/usr/bin/playercast"

# systemd related
DECKY_USER_HOME = os.environ.get("DECKY_USER_HOME", "/home/deck")
SERVICE_NAME = "decky-chromecast-receiver.service"
SYSTEMD_USER_DIR = Path(DECKY_USER_HOME) / ".config" / "systemd" / "user"

class Plugin:
    # A normal method. It can be called from the TypeScript side using @decky/api.
    async def add(self, left: int, right: int) -> int:
        return left + right

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        self.loop = asyncio.get_event_loop()
        decky.logger.info(f"Init plugin {PLUGIN_NAME}")
        await self._setup_playercast_service() # setup each time (should not conflict)
        await self.start_playercast() # attempt to start service

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky.logger.info(f"Migrating plugin {PLUGIN_NAME}")

    async def start_playercast(self):
        try:
            status = await self.get_status()

            # Start the service if not already running
            if not status["running"]:
                start_service_success, _, _ = await self._run_systemctl("start", SERVICE_NAME)


                if start_service_success:
                    # Wait a moment and check status again
                    await asyncio.sleep(1)
                    status = await self.get_status()
                    decky.logger.info(f"Plugin loaded successfully. Status: {status}")
                else:
                    decky.logger.error("Failed to start playercast service")
            else:
                decky.logger.info("Playercast service already running")
        except Exception as e:
            decky.logger.error(f"Failed start playercast systemd service: {SERVICE_NAME}: {e}", exc_info=True)
            return False

    async def stop_playercast(self):
        try:
            status = await self.get_status()

            # Start the service if not already running
            if not status["running"]:
                start_service_success, _, _ = await self._run_systemctl("stop", SERVICE_NAME)


                if start_service_success:
                    # Wait a moment and check status again
                    await asyncio.sleep(1)
                    status = await self.get_status()
                    decky.logger.info(f"Plugin loaded successfully. Status: {status}")
                else:
                    decky.logger.error("Failed to stop playercast service")
            else:
                decky.logger.info("Playercast service already running")
        except Exception as e:
            decky.logger.error(f"Failed stop playercast systemd service: {SERVICE_NAME}: {e}", exc_info=True)
            return False


    async def _setup_playercast_service(self):
        """
        Setup player cast systemd service for long running service that goes outside the lifetime of this plugin script
        """
        try:
            SYSTEMD_USER_DIR.mkdir(parents=True, exist_ok=True)
            service_path = SYSTEMD_USER_DIR / SERVICE_NAME
            with open(service_path, 'w') as f:
                f.write(self._player_cast_system_d_service_file_content())
            decky.logger.info(f"Created service file at {service_path} for plugin {PLUGIN_NAME}")
            return True
        except Exception as e:
            decky.logger.error(f"Failed to create service file: {e} for plugin {PLUGIN_NAME}", exc_info=True)
            return False

        try:
            # reload daemon so service file is applied
            daeomon_reloaed_success, _, _ = await self._run_systemctl("daemon-reload")
        except Exception as e:
            decky.logger.error(f"Failed to reload daemon: {e}", exc_info=True)
            return False


    async def _player_cast_system_d_service_file_content(self):
        return f"""
[Unit]
Description=Playercast Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Environment=DISPLAY=:0
ExecStart={PLAYER_CAST_BIN} -q -n '{PLAYER_CAST_NAME}' --player '{PLAYER_CAST_PLAYER}'
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
        """

    async def _run_systemctl(self, *args):
        """Run a systemctl --user command."""
        try:
            cmd = ["systemctl", "--user"] + list(args)
            decky.logger.info(f"Running: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._get_user_env()
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                decky.logger.error(f"systemctl command failed: {stderr.decode()}")
                return False, stdout.decode(), stderr.decode()

            return True, stdout.decode(), stderr.decode()

        except Exception as e:
            decky.logger.error(f"Failed to run systemctl: {e}", exc_info=True)
            return False, "", str(e)

    async def get_status(self):
        """Get the status of playercast service."""
        try:
            # Check if service is active
            success, stdout, _ = await self._run_systemctl("is-active", SERVICE_NAME)
            is_active = stdout.strip() == "active"

            # Check if service is enabled
            success, stdout, _ = await self._run_systemctl("is-enabled", SERVICE_NAME)
            is_enabled = stdout.strip() == "enabled"

            # Get detailed state
            _, stdout, _ = await self._run_systemctl("show", SERVICE_NAME, "--property=ActiveState", "--value")
            state = stdout.strip() or "unknown"

            return {
                "running": is_active,
                "enabled": is_enabled,
                "service": SERVICE_NAME,
                "state": state
            }

        except Exception as e:
            decky.logger.error(f"Error getting status: {e}", exc_info=True)
            return {"running": False, "enabled": False, "service": SERVICE_NAME, "state": "error"}