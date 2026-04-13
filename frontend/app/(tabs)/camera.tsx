import { CameraType, CameraView, useCameraPermissions } from "expo-camera";
import { useRef, useState, useEffect } from "react";
import { budgetStore, BUDGET_TIERS, BudgetTier } from "./budgetStore";
import {
  Pressable,
  StyleSheet,
  Text,
  View,
  Modal,
  Button,
  TextInput,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import FontAwesome6 from "@expo/vector-icons/FontAwesome6";
import { Image } from "expo-image";
import { pantryStore } from "./pantryStore";

const ACCENT = "#4ade80";

export default function Camera() {
  const [permission, requestPermission] = useCameraPermissions();
  const ref = useRef<CameraView>(null);
  const [uri, setUri] = useState<string | null>(null);
  const [facing, setFacing] = useState<CameraType>("back");
  const [budgetTier, setBudgetTier] = useState<BudgetTier | null>(null);
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [addedIngredients, setAddedIngredients] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<{
    ingredients: { name: string; category: string }[];
    matched_recipes: { name: string; match_score: { percentage: number } }[];
  } | null>(null);
  const [textMode, setTextMode] = useState(false);
  const [ingredientText, setIngredientText] = useState("");
  const [textAnalyzing, setTextAnalyzing] = useState(false);
  const [textResult, setTextResult] = useState<{
    ingredients: { name: string; category: string }[];
    matched_recipes: { name: string; match_score: { percentage: number } }[];
  } | null>(null);
  const [textAddedIngredients, setTextAddedIngredients] = useState(false);

  useEffect(() => {
    budgetStore.load().then((t) => {
      if (t) setBudgetTier(t);
    });
  }, []);

  if (!permission) return null;

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: "center", color: "#fff" }}>
          We need your permission to use the camera
        </Text>
        <Button onPress={requestPermission} title="Grant permission" />
      </View>
    );
  }

  const takePicture = async () => {
    const photo = await ref.current?.takePictureAsync();
    if (photo?.uri) setUri(photo.uri);
  };

  const toggleFacing = () => {
    setFacing((prev) => (prev === "back" ? "front" : "back"));
  };

  const analyzeImage = async (imageUri: string, tier: BudgetTier) => {
    setAnalyzing(true);
    try {
      const response = await fetch(imageUri);
      const blob = await response.blob();
      const base64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const result = reader.result as string;
          resolve(result.split(",")[1]);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });

      const res = await fetch(
        `${process.env.EXPO_PUBLIC_API_BASE_URL}/api/analyze`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image: base64, budget_tier: tier }),
        },
      );

      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setAnalysisResult(data);
    } catch (e: any) {
      alert("Analysis failed: " + e.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const analyzeText = async () => {
    if (!ingredientText.trim()) {
      alert("Please enter some ingredients first.");
      return;
    }
    setTextAnalyzing(true);
    try {
      const res = await fetch(
        `${process.env.EXPO_PUBLIC_API_BASE_URL}/api/analyze-text`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ingredients: ingredientText,
            budget_tier: budgetTier || "tier1",
          }),
        },
      );

      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setTextResult(data);
    } catch (e: any) {
      alert("Analysis failed: " + e.message);
    } finally {
      setTextAnalyzing(false);
    }
  };

  const renderTextMode = () => (
    <KeyboardAvoidingView
      style={styles.textModeContainer}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView contentContainerStyle={styles.textModeScroll}>
        <Text style={styles.textModeTitle}>📝 Enter Ingredients</Text>
        <Text style={styles.textModeSubtitle}>
          Type or paste your ingredients, separated by commas
        </Text>

        <TextInput
          style={styles.textInput}
          placeholder="e.g. chicken, rice, garlic, onion..."
          placeholderTextColor="#555"
          multiline
          value={ingredientText}
          onChangeText={setIngredientText}
        />

        {!textResult && (
          <View style={styles.textButtons}>
            <Pressable
              style={styles.previewBtn}
              onPress={() => {
                setTextMode(false);
                setTextResult(null);
                setIngredientText("");
                setTextAddedIngredients(false);
              }}
            >
              <Text style={styles.previewBtnText}>← Back to Camera</Text>
            </Pressable>
            <Pressable
              style={[
                styles.previewBtn,
                styles.previewBtnAccent,
                textAnalyzing && { opacity: 0.6 },
              ]}
              onPress={() => setShowBudgetModal(true)}
              disabled={textAnalyzing}
            >
              <Text style={[styles.previewBtnText, { color: "#000" }]}>
                {textAnalyzing ? "⏳ Matching..." : "🍽️ Find Recipes"}
              </Text>
            </Pressable>
          </View>
        )}

        {textAnalyzing && (
          <View style={{ alignItems: "center", gap: 8, marginTop: 16 }}>
            <Text style={{ color: "#888", fontSize: 13 }}>
              Finding recipes...
            </Text>
          </View>
        )}

        {textResult && (
          <View style={styles.analysisCard}>
            <Text style={styles.analysisTitle}>🥘 Ingredients</Text>
            <Text style={styles.analysisIngredients}>
              {textResult.ingredients.map((i) => i.name).join(", ")}
            </Text>
            <Text style={styles.analysisTitle}>🍽️ Matched Recipes</Text>
            {textResult.matched_recipes.length === 0 ? (
              <Text style={styles.analysisNone}>No recipes matched</Text>
            ) : (
              textResult.matched_recipes.map((r, i) => (
                <View key={i} style={styles.recipeRow}>
                  <Text style={styles.recipeName}>{r.name}</Text>
                  <Text style={styles.recipeScore}>
                    {r.match_score.percentage}%
                  </Text>
                </View>
              ))
            )}
            <View style={styles.resultButtons}>
              <Pressable
                style={[
                  styles.addButton,
                  textAddedIngredients && styles.addButtonDone,
                ]}
                onPress={() => {
                  if (textAddedIngredients) return;
                  textResult.ingredients.forEach((ing) => {
                    pantryStore.addItem(ing.category, ing.name);
                  });
                  setTextAddedIngredients(true);
                }}
              >
                <Text style={styles.addButtonText}>
                  {textAddedIngredients
                    ? "✓ Added to Pantry!"
                    : "Add Ingredients to Pantry"}
                </Text>
              </Pressable>
            </View>
            <Pressable
              style={[styles.previewBtn, { marginTop: 8 }]}
              onPress={() => {
                setTextResult(null);
                setIngredientText("");
                setTextAddedIngredients(false);
                setTextMode(false);
              }}
            >
              <Text style={styles.previewBtnText}>← Back to Camera</Text>
            </Pressable>
          </View>
        )}
      </ScrollView>

      <Modal
        transparent
        visible={showBudgetModal}
        animationType="slide"
        onRequestClose={() => setShowBudgetModal(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setShowBudgetModal(false)}
        >
          <View style={styles.budgetModal}>
            <Text style={styles.budgetModalTitle}>💰 Select Budget Tier</Text>
            <Text style={styles.budgetModalSubtitle}>
              This helps match affordable recipes
            </Text>
            {Object.values(BUDGET_TIERS).map((tier) => (
              <Pressable
                key={tier.value}
                style={[
                  styles.budgetOption,
                  budgetTier === tier.value && styles.budgetOptionSelected,
                ]}
                onPress={async () => {
                  const t = tier.value as BudgetTier;
                  setBudgetTier(t);
                  await budgetStore.save(t);
                  setShowBudgetModal(false);
                  analyzeText();
                }}
              >
                <Text style={styles.budgetOptionLabel}>{tier.label}</Text>
                <Text style={styles.budgetOptionDesc}>{tier.description}</Text>
                {budgetTier === tier.value && (
                  <Text style={styles.budgetOptionCheck}>✓</Text>
                )}
              </Pressable>
            ))}
          </View>
        </Pressable>
      </Modal>
    </KeyboardAvoidingView>
  );

  const renderPicture = (uri: string) => (
    <View style={styles.previewContainer}>
      <Image
        source={{ uri }}
        contentFit="contain"
        style={styles.previewImage}
      />

      {!analysisResult && (
        <View style={styles.previewButtons}>
          <Pressable
            style={styles.previewBtn}
            onPress={() => {
              setUri(null);
              setAnalysisResult(null);
              setAddedIngredients(false);
            }}
          >
            <Text style={styles.previewBtnText}>📷 Retake</Text>
          </Pressable>
          <Pressable
            style={[
              styles.previewBtn,
              styles.previewBtnAccent,
              analyzing && { opacity: 0.6 },
            ]}
            onPress={() => setShowBudgetModal(true)}
            disabled={analyzing}
          >
            <Text style={[styles.previewBtnText, { color: "#000" }]}>
              {analyzing ? "⏳ Analyzing..." : "🤖 Analyze Food"}
            </Text>
          </Pressable>
        </View>
      )}

      {analyzing && (
        <View style={{ alignItems: "center", gap: 8 }}>
          <Text style={{ color: "#888", fontSize: 13 }}>
            Analyzing Image...
          </Text>
          <Text style={{ color: "#555", fontSize: 12 }}>
            This may take 5-10 seconds
          </Text>
        </View>
      )}

      {analysisResult && (
        <View style={styles.analysisCard}>
          <Text style={styles.analysisTitle}>🥘 Ingredients Found</Text>
          <Text style={styles.analysisIngredients}>
            {analysisResult.ingredients.map((i) => i.name).join(", ")}
          </Text>
          <Text style={styles.analysisTitle}>🍽️ Matched Recipes</Text>
          {analysisResult.matched_recipes.length === 0 ? (
            <Text style={styles.analysisNone}>No recipes matched</Text>
          ) : (
            analysisResult.matched_recipes.map((r, i) => (
              <View key={i} style={styles.recipeRow}>
                <Text style={styles.recipeName}>{r.name}</Text>
                <Text style={styles.recipeScore}>
                  {r.match_score.percentage}%
                </Text>
              </View>
            ))
          )}
          <View style={styles.resultButtons}>
            <Pressable
              style={[
                styles.addButton,
                addedIngredients && styles.addButtonDone,
              ]}
              onPress={() => {
                if (addedIngredients) return;
                analysisResult.ingredients.forEach((ing) => {
                  pantryStore.addItem(ing.category, ing.name);
                });
                setAddedIngredients(true);
              }}
            >
              <Text style={styles.addButtonText}>
                {addedIngredients
                  ? "✓ Added to Pantry!"
                  : "Add Ingredients to Pantry"}
              </Text>
            </Pressable>
          </View>
          <Pressable
            style={[styles.previewBtn, { marginTop: 8 }]}
            onPress={() => {
              setUri(null);
              setAnalysisResult(null);
              setAddedIngredients(false);
            }}
          >
            <Text style={styles.previewBtnText}>📷 Take Another</Text>
          </Pressable>
        </View>
      )}

      <Modal
        transparent
        visible={showBudgetModal}
        animationType="slide"
        onRequestClose={() => setShowBudgetModal(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setShowBudgetModal(false)}
        >
          <View style={styles.budgetModal}>
            <Text style={styles.budgetModalTitle}>💰 Select Budget Tier</Text>
            <Text style={styles.budgetModalSubtitle}>
              This helps the AI suggest affordable recipes
            </Text>
            {Object.values(BUDGET_TIERS).map((tier) => (
              <Pressable
                key={tier.value}
                style={[
                  styles.budgetOption,
                  budgetTier === tier.value && styles.budgetOptionSelected,
                ]}
                onPress={async () => {
                  const t = tier.value as BudgetTier;
                  setBudgetTier(t);
                  await budgetStore.save(t);
                  setShowBudgetModal(false);
                  analyzeImage(uri, t);
                }}
              >
                <Text style={styles.budgetOptionLabel}>{tier.label}</Text>
                <Text style={styles.budgetOptionDesc}>{tier.description}</Text>
                {budgetTier === tier.value && (
                  <Text style={styles.budgetOptionCheck}>✓</Text>
                )}
              </Pressable>
            ))}
          </View>
        </Pressable>
      </Modal>
    </View>
  );

  const renderCamera = () => (
    <View style={styles.cameraContainer}>
      <CameraView
        style={styles.camera}
        ref={ref}
        facing={facing}
        responsiveOrientationWhenOrientationLocked
      />
      <Pressable style={styles.textModeBtn} onPress={() => setTextMode(true)}>
        <Text style={styles.textModeBtnText}>📝 Type Ingredients</Text>
      </Pressable>
      <View style={styles.shutterContainer}>
        <Pressable onPress={toggleFacing}>
          <FontAwesome6 name="rotate-left" size={28} color="white" />
        </Pressable>
        <Pressable onPress={takePicture}>
          {({ pressed }) => (
            <View style={[styles.shutterBtn, { opacity: pressed ? 0.5 : 1 }]}>
              <View style={styles.shutterBtnInner} />
            </View>
          )}
        </Pressable>
        <View style={{ width: 28 }} />
      </View>
    </View>
  );

  if (textMode) return renderTextMode();

  return (
    <View style={styles.container}>
      {uri ? renderPicture(uri) : renderCamera()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
    alignItems: "center",
    justifyContent: "center",
  },
  cameraContainer: StyleSheet.absoluteFillObject,
  camera: StyleSheet.absoluteFillObject,
  textModeBtn: {
    position: "absolute",
    top: 52,
    left: 16,
    backgroundColor: "rgba(0,0,0,0.5)",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.15)",
  },
  textModeBtnText: { color: "#fff", fontSize: 13, fontWeight: "600" },
  shutterContainer: {
    position: "absolute",
    bottom: 44,
    left: 0,
    width: "100%",
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-evenly",
    paddingHorizontal: 30,
  },
  shutterBtn: {
    backgroundColor: "transparent",
    borderWidth: 5,
    borderColor: "white",
    width: 85,
    height: 85,
    borderRadius: 45,
    alignItems: "center",
    justifyContent: "center",
  },
  shutterBtnInner: {
    width: 70,
    height: 70,
    borderRadius: 50,
    backgroundColor: "white",
  },
  previewContainer: {
    flex: 1,
    backgroundColor: "#000",
    alignItems: "center",
    justifyContent: "center",
    gap: 20,
  },
  previewImage: { width: "100%", aspectRatio: 1 },
  previewButtons: { flexDirection: "row", gap: 12, paddingHorizontal: 24 },
  previewBtn: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    backgroundColor: "rgba(255,255,255,0.08)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
  },
  previewBtnAccent: { backgroundColor: ACCENT, borderColor: ACCENT },
  previewBtnText: { color: "#fff", fontWeight: "600", fontSize: 14 },
  analysisCard: {
    width: "100%",
    backgroundColor: "#1a1a2e",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    gap: 8,
  },
  analysisTitle: {
    color: ACCENT,
    fontWeight: "bold",
    fontSize: 15,
    marginTop: 10,
  },
  analysisIngredients: { color: "#ccc", fontSize: 13, lineHeight: 20 },
  analysisNone: { color: "#555", fontSize: 13 },
  recipeRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: "#2a2a3e",
  },
  recipeName: { color: "#fff", fontSize: 14, fontWeight: "500" },
  recipeScore: { color: ACCENT, fontSize: 14, fontWeight: "bold" },
  resultButtons: { flexDirection: "row", gap: 12, marginTop: 20 },
  addButton: {
    flex: 1,
    backgroundColor: ACCENT,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  addButtonDone: {
    backgroundColor: "#2a2a3e",
    borderWidth: 1,
    borderColor: ACCENT,
  },
  addButtonText: { color: "#000", fontWeight: "bold", fontSize: 15 },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.4)" },
  budgetModal: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "#1a1a2e",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40,
    gap: 12,
  },
  budgetModalTitle: { color: "#fff", fontSize: 20, fontWeight: "bold" },
  budgetModalSubtitle: { color: "#555", fontSize: 13, marginBottom: 8 },
  budgetOption: {
    backgroundColor: "rgba(255,255,255,0.05)",
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  budgetOptionSelected: {
    borderColor: ACCENT,
    backgroundColor: "rgba(74,222,128,0.08)",
  },
  budgetOptionLabel: { color: "#fff", fontWeight: "600", fontSize: 15 },
  budgetOptionDesc: { color: "#888", fontSize: 13 },
  budgetOptionCheck: { color: ACCENT, fontSize: 18, fontWeight: "bold" },
  textModeContainer: { flex: 1, backgroundColor: "#0d0d1a" },
  textModeScroll: { padding: 24, gap: 16, paddingBottom: 60 },
  textModeTitle: {
    color: "#fff",
    fontSize: 22,
    fontWeight: "800",
    marginTop: 20,
  },
  textModeSubtitle: { color: "#555", fontSize: 14, marginBottom: 8 },
  textInput: {
    backgroundColor: "rgba(255,255,255,0.05)",
    borderRadius: 14,
    padding: 16,
    color: "#fff",
    fontSize: 15,
    minHeight: 120,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.1)",
    textAlignVertical: "top",
  },
  textButtons: { flexDirection: "row", gap: 12 },
});
