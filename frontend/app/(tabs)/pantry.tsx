import {
  Text,
  View,
  StyleSheet,
  FlatList,
  Pressable,
  ScrollView,
} from "react-native";
import { useEffect, useState } from "react";
import { LinearGradient } from "expo-linear-gradient";
import { pantryStore } from "./pantryStore";

const ACCENT = "#4ade80";

export default function PantryScreen() {
  const [items, setItems] = useState(pantryStore.getItems());
  const [savedRecipes, setSavedRecipes] = useState(
    pantryStore.getSavedRecipes(),
  );
  const [expandedRecipe, setExpandedRecipe] = useState<string | null>(null);

  useEffect(() => {
    const unsub = pantryStore.subscribe(() => {
      setItems([...pantryStore.getItems()]);
      setSavedRecipes([...pantryStore.getSavedRecipes()]);
    });
    return unsub;
  }, []);

  return (
    <LinearGradient
      colors={["#0f0c29", "#1a1a40", "#0d0d1a"]}
      style={styles.container}
      start={{ x: 0.2, y: 0 }}
      end={{ x: 0.8, y: 1 }}
    >
      <ScrollView contentContainerStyle={{ paddingBottom: 40 }}>
        {/* Saved Recipes */}
        <Text style={styles.title}>Saved Recipes</Text>
        <Text style={styles.subtitle}>
          {savedRecipes.length} recipe{savedRecipes.length !== 1 ? "s" : ""}
        </Text>

        {savedRecipes.length === 0 ? (
          <View style={styles.emptySmall}>
            <Text style={styles.emptySubtext}>
              No saved recipes yet. Use a recipe from the camera screen to save
              it here.
            </Text>
          </View>
        ) : (
          savedRecipes.map((recipe) => {
            const isExpanded = expandedRecipe === recipe.id;
            return (
              <View key={recipe.id} style={styles.recipeCard}>
                <Pressable
                  style={styles.recipeHeader}
                  onPress={() =>
                    setExpandedRecipe(isExpanded ? null : recipe.id)
                  }
                >
                  <View style={{ flex: 1 }}>
                    <Text style={styles.recipeName}>{recipe.name}</Text>
                    <Text style={styles.recipeDate}>{recipe.savedAt}</Text>
                  </View>
                  <View style={{ alignItems: "flex-end", gap: 4 }}>
                    <Text style={{ color: "#555", fontSize: 12 }}>
                      {isExpanded ? "▲ hide" : "▼ view"}
                    </Text>
                    <Pressable
                      onPress={() => pantryStore.removeRecipe(recipe.id)}
                    >
                      <Text style={styles.deleteText}>✕</Text>
                    </Pressable>
                  </View>
                </Pressable>

                {isExpanded && (
                  <View style={styles.recipeDetails}>
                    <Text style={styles.recipeDetailLabel}>🛒 Ingredients</Text>
                    {recipe.ingredients.map((ing, i) => (
                      <Text key={i} style={styles.recipeDetailItem}>
                        • {ing}
                      </Text>
                    ))}
                    <Text style={[styles.recipeDetailLabel, { marginTop: 12 }]}>
                      📋 Instructions
                    </Text>
                    <Text style={styles.recipeDetailText}>
                      {recipe.instructions}
                    </Text>
                  </View>
                )}
              </View>
            );
          })
        )}

        {/* Pantry Items */}
        <Text style={[styles.title, { marginTop: 24 }]}>My Pantry</Text>
        <Text style={styles.subtitle}>
          {items.length} item{items.length !== 1 ? "s" : ""}
        </Text>

        {items.length === 0 ? (
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>🧊</Text>
            <Text style={styles.emptyText}>Your pantry is empty</Text>
            <Text style={styles.emptySubtext}>
              Use a recipe from the camera screen to add items
            </Text>
          </View>
        ) : (
          items.map((item) => (
            <View key={item.id} style={styles.card}>
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
          ))
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
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
  emptySmall: {
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  empty: {
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    paddingVertical: 24,
  },
  emptyIcon: { fontSize: 52 },
  emptyText: { color: "#fff", fontSize: 18, fontWeight: "bold" },
  emptySubtext: { color: "#555", fontSize: 14 },
  recipeCard: {
    backgroundColor: "rgba(255,255,255,0.05)",
    borderRadius: 14,
    marginHorizontal: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.07)",
    overflow: "hidden",
  },
  recipeHeader: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
  },
  recipeName: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  recipeDate: { color: "#444", fontSize: 12, marginTop: 2 },
  recipeDetails: {
    padding: 16,
    paddingTop: 0,
    borderTopWidth: 1,
    borderTopColor: "rgba(255,255,255,0.06)",
  },
  recipeDetailLabel: {
    color: ACCENT,
    fontWeight: "600",
    fontSize: 13,
    marginBottom: 6,
  },
  recipeDetailItem: { color: "#ccc", fontSize: 13, lineHeight: 22 },
  recipeDetailText: { color: "#ccc", fontSize: 13, lineHeight: 20 },
  card: {
    backgroundColor: "rgba(255,255,255,0.05)",
    borderRadius: 14,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 10,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.07)",
  },
  cardLeft: { flex: 1, gap: 4 },
  cardType: {
    color: ACCENT,
    fontSize: 11,
    fontWeight: "bold",
    letterSpacing: 1,
  },
  cardData: { color: "#fff", fontSize: 16, fontWeight: "600" },
  cardDate: { color: "#444", fontSize: 12 },
  deleteBtn: { padding: 8 },
  deleteText: { color: "#555", fontSize: 16 },
});
