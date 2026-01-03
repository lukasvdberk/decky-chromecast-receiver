import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  staticClasses
} from "@decky/ui";
import {
  removeEventListener,
  callable,
  definePlugin,
  toaster,
} from "@decky/api"
import { FaShip } from "react-icons/fa";
import { useCallback, useEffect, useState } from "react";

// Service status from backend
export interface ServiceStatus {
  running: boolean;
  enabled: boolean;
  service: string;
  state: string;
}

const startService = callable<[], boolean>("start_playercast");
const stopService = callable<[], boolean>("stop_playercast");
const getStatus = callable<[], ServiceStatus>("get_status");

function Content() {
  const [status, setStatus] = useState<ServiceStatus | null>(null);

  
  const refreshStatus = useCallback(async () => {
    try {
      const newStatus = await getStatus();
      setStatus(newStatus);
    } catch (error) {
      console.error("Failed to get status:", error);
      toaster.toast({
        title: "Failed to get casting service status",
        body: "Failed to get casting service status"
      });
    }
  }, []);

  const startServiceOnClick = useCallback(async () => {
    const success = await startService();
    
    toaster.toast({
      title: success ? "Chromecast started" : "Failed to start",
      body: success ? "The steam deck is ready for casting content." : "Failed to start service for casting, try again later"
    });

    await refreshStatus();
  }, [refreshStatus]);

  const stopServiceOnClick = useCallback(async () => {
    const success = await stopService();
    
    toaster.toast({
      title: success ? "Chromecast stopped" : "Failed to stop",
      body: success ? "Stopped casting servcie" : "Failed to stop service for casting, try again later"
    });

    await refreshStatus();
  }, [refreshStatus]);

  useEffect(() => {
    const loadInitialStatus = async () => {
      await refreshStatus();
    };

    loadInitialStatus();
  }, [refreshStatus]);
  
  return (
    <PanelSection title="Panel Section">
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={startServiceOnClick}
        >
          { "Start casting" }
        </ButtonItem>
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={stopServiceOnClick}
        >
          {"Stop casting"}
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
};

export default definePlugin(() => {
  console.log("Template plugin initializing, this is called once on frontend startup")

  return {
    // The name shown in various decky menus
    name: "Chromecast Receiver",
    // The element displayed at the top of your plugin's menu
    titleView: <div className={staticClasses.Title}>Chromecast Receiver</div>,
    // The content of your plugin's menu
    content: <Content />,
    // The icon displayed in the plugin list
    icon: <FaShip />,
    // The function triggered when your plugin unloads
    onDismount() {
      console.log("Unloading")
      removeEventListener("timer_event", listener);
      // serverApi.routerHook.removeRoute("/decky-plugin-test");
    },
  };
});
