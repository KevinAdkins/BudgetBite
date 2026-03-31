import { Text, View, StyleSheet, FlatList, Pressable } from "react-native";
import { useEffect, useState } from "react";
import { LinearGradient } from "expo-linear-gradient";
import { pantryStore } from "./pantryStore";

const ACCENT = "#4ade80";

export default function PantryScreen() {
  const [items, setItems] = useState(pantryStore.getItems());

  useEffect(() => {
    const unsub = pantryStore.subscribe(() =>
      setItems([...pantryStore.getItems()]),
    );
    return unsub;
  }, []);

  return (
    <LinearGradient
      colors={["#0f0c29", "#1a1a40", "#0d0d1a"]}
      style={styles.container}
      start={{ x: 0.2, y: 0 }}
      end={{ x: 0.8, y: 1 }}
    >
      <Text style={styles.title}>My Pantry</Text>
      <Text style={styles.subtitle}>
        {items.length} item{items.length !== 1 ? "s" : ""}
      </Text>
      {items.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>🧊</Text>
          <Text style={styles.emptyText}>Your pantry is empty</Text>
          <Text style={styles.emptySubtext}>Take a photo to get started!</Text>
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ padding: 16, gap: 12 }}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.cardLeft}>
                <Text style={styles.cardType}>{item.type.toUpperCase()}</Text>
                <Text style={styles.cardData} numberOfLines={1}>
                  {item.data}
                </Text>
                <Text style={styles.cardDate}>{item.addedAt}</Text>
              </View>
              <Pressable
                onPress={() => pantryStore.removeItem(item.id)}
                style={styles.deleteBtn}
              >
                <Text style={styles.deleteText}>✕</Text>
              </Pressable>
            </View>
          )}
        />
      )}
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  title: {
    fontSize: 28,
    fontWeight: "800",
    color: "#fff",
    paddingHorizontal: 20,
    paddingTop: 24,
  },
  subtitle: {
    fontSize: 13,
    color: "#555",
    paddingHorizontal: 20,
    marginBottom: 8,
    marginTop: 2,
  },
  empty: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  emptyIcon: {
    fontSize: 52,
  },
  emptyText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
  emptySubtext: {
    color: "#555",
    fontSize: 14,
  },
  card: {
    backgroundColor: "rgba(255,255,255,0.05)",
    borderRadius: 14,
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.07)",
  },
  cardLeft: {
    flex: 1,
    gap: 4,
  },
  cardType: {
    color: ACCENT,
    fontSize: 11,
    fontWeight: "bold",
    letterSpacing: 1,
  },
  cardData: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  cardDate: {
    color: "#444",
    fontSize: 12,
  },
  deleteBtn: {
    padding: 8,
  },
  deleteText: {
    color: "#555",
    fontSize: 16,
  },
});
