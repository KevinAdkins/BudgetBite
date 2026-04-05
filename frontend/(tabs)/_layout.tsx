import { Tabs } from "expo-router";
import Ionicons from "@expo/vector-icons/Ionicons";
import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#4ade80",
        tabBarInactiveTintColor: "#555",
        headerStyle: { backgroundColor: "#0f0c29" },
        headerShadowVisible: false,
        headerTitleStyle: { color: "#fff" },
        tabBarStyle: {
          backgroundColor: "#0d0d1a",
          borderTopColor: "rgba(255,255,255,0.06)",
          borderTopWidth: 1,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color }) => (
            <Ionicons name="home-outline" size={24} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="pantry"
        options={{
          title: "Pantry",
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="fridge" size={24} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="camera"
        options={{
          title: "Camera",
          tabBarIcon: ({ color }) => (
            <Ionicons name="camera-outline" size={24} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
