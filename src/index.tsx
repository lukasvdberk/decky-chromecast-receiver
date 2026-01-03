import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  staticClasses
} from "@decky/ui";
import {
  addEventListener,
  removeEventListener,
  callable,
  definePlugin,
  toaster,
} from "@decky/api"
import { FaShip } from "react-icons/fa";

// import logo from "../assets/logo.png";

const startService = callable<[], boolean>("start_playercast");
const stopService = callable<[], boolean>("stop_playercast");

function Content() {
  const startServiceOnClick = async () => {
    const success = await startService();
    
    toaster.toast({
      title: success ? "Chromecast started" : "Failed to start",
      body: success ? "The steam deck is ready for casting content." : "Failed to start service for casting, try again later"
    });
  };

  const stopServiceOnClick = async () => {
    const success = await stopService();
    
    toaster.toast({
      title: success ? "Chromecast stopped" : "Failed to stop",
      body: success ? "Stopped casting servcie" : "Failed to stop service for casting, try again later"
    });
  };
  
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

  // serverApi.routerHook.addRoute("/decky-plugin-test", DeckyPluginRouterTest, {
  //   exact: true,
  // });

  // Add an event listener to the "timer_event" event from the backend
  const listener = addEventListener<[
    test1: string,
    test2: boolean,
    test3: number
  ]>("timer_event", (test1, test2, test3) => {
    console.log("Template got timer_event with:", test1, test2, test3)
    toaster.toast({
      title: "template got timer_event",
      body: `${test1}, ${test2}, ${test3}`
    });
  });

  return {
    // The name shown in various decky menus
    name: "Test Plugin",
    // The element displayed at the top of your plugin's menu
    titleView: <div className={staticClasses.Title}>Decky Example Plugin</div>,
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
