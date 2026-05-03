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

type MatchedRecipe = {
  name: string;
  category: string;
  ingredients: string;
  instructions: string;
  match_score: { percentage: number };
};

type AnalysisResult = {
  ingredients: { name: string; category: string }[];
  matched_recipes: MatchedRecipe[];
  generated_recipe?: string;
  generated_recipe_pricing?: {
    estimatedTotal?: number;
    subtotal?: number;
  } | null;
  generated_recipe_pricing_ingredients?: string[];
  recipe_over_budget?: boolean;
  recipe_under_budget?: boolean;
  budget_limit?: number | null;
  generation_attempts?: number;
  regeneration_requested?: boolean;
  regeneration_prompt?: string | null;
  can_regenerate?: boolean;
};

export default function Camera() {
  const [permission, requestPermission] = useCameraPermissions();
  const ref = useRef<CameraView>(null);
  const [uri, setUri] = useState<string | null>(null);
  const [facing, setFacing] = useState<CameraType>("back");
  const [budgetTier, setBudgetTier] = useState<BudgetTier | null>(null);
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [addedIngredients, setAddedIngredients] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null,
  );
  const [expandedRecipe, setExpandedRecipe] = useState<string | null>(null);
  const [textMode, setTextMode] = useState(false);
  const [ingredientText, setIngredientText] = useState("");
  const [textAnalyzing, setTextAnalyzing] = useState(false);
  const [textResult, setTextResult] = useState<AnalysisResult | null>(null);
  const [textAddedIngredients, setTextAddedIngredients] = useState(false);
  const [textExpandedRecipe, setTextExpandedRecipe] = useState<string | null>(
    null,
  );

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

  const analyzeImage = async (
    imageUri: string,
    tier: BudgetTier,
    opts?: { regenerate?: boolean; max_regeneration_attempts?: number },
  ) => {
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
          body: JSON.stringify({
            image: base64,
            budget_tier: tier,
            regenerate_recipe: Boolean(opts?.regenerate),
            max_regeneration_attempts: opts?.max_regeneration_attempts ?? 3,
          }),
        },
      );

      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setAnalysisResult(data);
      setExpandedRecipe(null);
    } catch (e: any) {
      alert("Analysis failed: " + e.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const analyzeText = async (opts?: {
    regenerate?: boolean;
    max_regeneration_attempts?: number;
  }) => {
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
            regenerate_recipe: Boolean(opts?.regenerate),
            max_regeneration_attempts: opts?.max_regeneration_attempts ?? 3,
          }),
        },
      );

      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setTextResult(data);
      setTextExpandedRecipe(null);
    } catch (e: any) {
      alert("Analysis failed: " + e.message);
    } finally {
      setTextAnalyzing(false);
    }
  };

  const formatCurrency = (value?: number | null) => {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return null;
    }
    return `$${value.toFixed(2)}`;
  };

  const getEstimatedTotal = (result: AnalysisResult) => {
    const pricing = result.generated_recipe_pricing;
    if (!pricing) return null;
    return pricing.estimatedTotal ?? pricing.subtotal ?? null;
  };

  const renderBudgetSummary = (
    result: AnalysisResult,
    onRegenerate?: () => void,
  ) => {
    const estimatedTotal = getEstimatedTotal(result);
    const budgetLimit = formatCurrency(result.budget_limit ?? null);
    const estimatedLabel = formatCurrency(estimatedTotal);
    const statusLabel = result.recipe_over_budget
      ? "Over budget"
      : result.recipe_under_budget
        ? "Below target range"
        : estimatedTotal !== null
          ? "Within budget"
          : "Not priced yet";

    return (
      <View style={styles.budgetSummaryCard}>
        <Text style={styles.budgetSummaryTitle}>💰 Budget Check</Text>
        <View style={styles.budgetSummaryRow}>
          <Text style={styles.budgetSummaryLabel}>Using budget</Text>
          <Text style={styles.budgetSummaryValue}>
            {budgetTier ? BUDGET_TIERS[budgetTier].label : "None"}
          </Text>
        </View>
        <Text style={styles.budgetSummaryStatus}>{statusLabel}</Text>

        <View style={styles.budgetSummaryRow}>
          <Text style={styles.budgetSummaryLabel}>Estimated total</Text>
          <Text style={styles.budgetSummaryValue}>
            {estimatedLabel ?? "Unavailable"}
          </Text>
        </View>

        <View style={styles.budgetSummaryRow}>
          <Text style={styles.budgetSummaryLabel}>Budget limit</Text>
          <Text style={styles.budgetSummaryValue}>
            {budgetLimit ?? "No upper limit"}
          </Text>
        </View>

        <View style={styles.budgetSummaryRow}>
          <Text style={styles.budgetSummaryLabel}>Generation attempts</Text>
          <Text style={styles.budgetSummaryValue}>
            {typeof result.generation_attempts === "number"
              ? String(result.generation_attempts)
              : "0"}
          </Text>
        </View>

        {result.regeneration_prompt ? (
          <Text style={styles.budgetSummaryPrompt}>
            {result.regeneration_prompt}
          </Text>
        ) : null}

        {result.can_regenerate ? (
          <>
            <Text style={styles.budgetSummaryHint}>
              You can regenerate this recipe with a higher attempt limit.
            </Text>
            {onRegenerate ? (
              <Pressable
                style={[
                  styles.previewBtn,
                  styles.previewBtnAccent,
                  { marginTop: 8 },
                ]}
                onPress={() => onRegenerate()}
              >
                <Text style={[styles.previewBtnText, { color: "#000" }]}>
                  🔁 Regenerate Recipe
                </Text>
              </Pressable>
            ) : null}
          </>
        ) : null}
      </View>
    );
  };

  const sanitizeGeneratedRecipe = (recipeText?: string) => {
    if (!recipeText) return "";
    return recipeText
      .split("\n")
      .filter((line) => {
        const normalized = line.trim().toLowerCase();
        if (!normalized) return true;
        if (normalized.startsWith("total estimated cost:")) return false;
        if (normalized.includes("budget-friendly:")) return false;
        if (normalized.includes("premium selection:")) return false;
        if (normalized.startsWith("------------------------------"))
          return false;
        return true;
      })
      .join("\n")
      .trim();
  };

  const parseGeneratedRecipe = (recipeText?: string) => {
    const sanitized = sanitizeGeneratedRecipe(recipeText);
    if (!sanitized) return null;

    const lines = sanitized
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    const sectionIndex = (prefix: string) =>
      lines.findIndex((line) => line.toLowerCase().startsWith(prefix));

    const nameLine = lines.find((line) =>
      line.toLowerCase().startsWith("recipe name:"),
    );
    const name = nameLine
      ? nameLine.split(":").slice(1).join(":").trim()
      : "Generated Recipe";

    const ingredientsStart = sectionIndex("ingredients:");
    const instructionsStart = sectionIndex("instructions:");
    const notesStart = sectionIndex("chef's notes:");

    const ingredientsEnd =
      instructionsStart > -1
        ? instructionsStart
        : notesStart > -1
          ? notesStart
          : lines.length;

    const instructionsEnd = notesStart > -1 ? notesStart : lines.length;

    const ingredients =
      ingredientsStart > -1
        ? lines
            .slice(ingredientsStart + 1, ingredientsEnd)
            .map((line) =>
              line.replace(/^\s*(?:[•*-]\s+|\d+[.)]\s+)?/, "").trim(),
            )
            .filter(Boolean)
        : [];

    const instructions =
      instructionsStart > -1
        ? lines
            .slice(instructionsStart + 1, instructionsEnd)
            .map((line) =>
              line.replace(/^\s*(?:[•*-]\s+|\d+[.)]\s+)?/, "").trim(),
            )
            .filter(Boolean)
            .join("\n")
        : "";

    if (!ingredients.length || !instructions) {
      return null;
    }

    return { name, ingredients, instructions };
  };

  const saveGeneratedRecipe = (
    result: AnalysisResult,
    markSaved: (value: boolean) => void,
    alreadySaved: boolean,
  ) => {
    if (alreadySaved) return;

    const parsedRecipe = parseGeneratedRecipe(result.generated_recipe);
    if (!parsedRecipe) {
      return;
    }

    parsedRecipe.ingredients.forEach((ingredient) => {
      pantryStore.addItem("recipe", ingredient);
    });
    pantryStore.saveRecipe(
      parsedRecipe.name,
      parsedRecipe.ingredients,
      parsedRecipe.instructions,
    );
    markSaved(true);
    alert(
      `✓ Saved \"${parsedRecipe.name}\" with ${parsedRecipe.ingredients.length} ingredients to pantry!`,
    );
  };

  const hasSavableGeneratedRecipe = (result: AnalysisResult) =>
    Boolean(parseGeneratedRecipe(result.generated_recipe));

  const renderRecipeList = (
    recipes: MatchedRecipe[],
    expandedName: string | null,
    setExpanded: (name: string | null) => void,
  ) => {
    if (recipes.length === 0) {
      return <Text style={styles.analysisNone}>No recipes matched</Text>;
    }
    return recipes.map((r, i) => {
      const isExpanded = expandedName === r.name;
      const ingredientList = r.ingredients
        .split(",")
        .map((ing) => ing.trim())
        .filter(Boolean);

      return (
        <View key={i} style={styles.recipeCard}>
          <Pressable
            style={styles.recipeHeader}
            onPress={() => setExpanded(isExpanded ? null : r.name)}
          >
            <View style={{ flex: 1 }}>
              <Text style={styles.recipeName}>{r.name}</Text>
              <Text style={styles.recipeCategory}>{r.category}</Text>
            </View>
            <View style={{ alignItems: "flex-end", gap: 4 }}>
              <Text style={styles.recipeScore}>
                {r.match_score.percentage}%
              </Text>
              <Text style={{ color: "#555", fontSize: 12 }}>
                {isExpanded ? "▲ hide" : "▼ details"}
              </Text>
            </View>
          </Pressable>

          {isExpanded && (
            <View style={styles.recipeDetails}>
              <Text style={styles.recipeDetailLabel}>
                🛒 Ingredients Needed
              </Text>
              {ingredientList.map((ing, j) => (
                <Text key={j} style={styles.recipeDetailItem}>
                  • {ing}
                </Text>
              ))}
              <Text style={[styles.recipeDetailLabel, { marginTop: 12 }]}>
                📋 Instructions
              </Text>
              <Text style={styles.recipeDetailText}>{r.instructions}</Text>

              <Pressable
                style={styles.useRecipeBtn}
                onPress={() => {
                  ingredientList.forEach((ing) => {
                    pantryStore.addItem("recipe", ing);
                  });
                  pantryStore.saveRecipe(
                    r.name,
                    ingredientList,
                    r.instructions,
                  );
                  alert(
                    `✓ Added ${ingredientList.length} ingredients from "${r.name}" to your pantry!`,
                  );
                }}
              >
                <Text style={styles.useRecipeBtnText}>🛒 Use This Recipe</Text>
              </Pressable>
            </View>
          )}
        </View>
      );
    });
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
            {renderBudgetSummary(textResult, () =>
              analyzeText({ regenerate: true, max_regeneration_attempts: 3 }),
            )}
            <Text style={styles.analysisTitle}>🍽️ Matched Recipes</Text>
            {renderRecipeList(
              textResult.matched_recipes,
              textExpandedRecipe,
              setTextExpandedRecipe,
            )}
            {textResult.generated_recipe ? (
              <View style={{ marginTop: 12 }}>
                <Text style={styles.analysisTitle}>🍳 Generated Recipe</Text>
                <Text
                  style={{
                    color: "#ccc",
                    fontSize: 13,
                    lineHeight: 20,
                    marginTop: 6,
                  }}
                >
                  {sanitizeGeneratedRecipe(textResult.generated_recipe)}
                </Text>
              </View>
            ) : null}
            {hasSavableGeneratedRecipe(textResult) ? (
              <View style={styles.resultButtons}>
                <Pressable
                  style={[
                    styles.addButton,
                    textAddedIngredients && styles.addButtonDone,
                  ]}
                  onPress={() =>
                    saveGeneratedRecipe(
                      textResult,
                      setTextAddedIngredients,
                      textAddedIngredients,
                    )
                  }
                  disabled={textAddedIngredients}
                >
                  <Text style={styles.addButtonText}>
                    {textAddedIngredients
                      ? "✓ Generated Recipe Saved!"
                      : "Save Generated Recipe"}
                  </Text>
                </Pressable>
              </View>
            ) : null}
            <Pressable
              style={[styles.previewBtn, { marginTop: 8 }]}
              onPress={() => {
                setTextResult(null);
                setIngredientText("");
                setTextAddedIngredients(false);
                setTextExpandedRecipe(null);
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
      {!analysisResult && (
        <>
          <Image
            source={{ uri }}
            contentFit="contain"
            style={styles.previewImage}
          />
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
        </>
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
        <ScrollView
          style={{ width: "100%", flex: 1 }}
          contentContainerStyle={styles.analysisCard}
          nestedScrollEnabled
        >
          <Text style={styles.analysisTitle}>🥘 Ingredients Found</Text>
          <Text style={styles.analysisIngredients}>
            {analysisResult.ingredients.map((i) => i.name).join(", ")}
          </Text>
          {renderBudgetSummary(analysisResult, () =>
            analyzeImage(uri, (budgetTier as BudgetTier) || "tier1", {
              regenerate: true,
              max_regeneration_attempts: 3,
            }),
          )}
          <Text style={styles.analysisTitle}>🍽️ Matched Recipes</Text>
          {renderRecipeList(
            analysisResult.matched_recipes,
            expandedRecipe,
            setExpandedRecipe,
          )}
          {analysisResult.generated_recipe && (
            <View style={{ marginTop: 12 }}>
              <Text style={styles.analysisTitle}>🍳 Generated Recipe</Text>
              <Text
                style={{
                  color: "#ccc",
                  fontSize: 13,
                  lineHeight: 20,
                  marginTop: 6,
                }}
              >
                {sanitizeGeneratedRecipe(analysisResult.generated_recipe)}
              </Text>
            </View>
          )}
          {hasSavableGeneratedRecipe(analysisResult) ? (
            <View style={styles.resultButtons}>
              <Pressable
                style={[
                  styles.addButton,
                  addedIngredients && styles.addButtonDone,
                ]}
                onPress={() =>
                  saveGeneratedRecipe(
                    analysisResult,
                    setAddedIngredients,
                    addedIngredients,
                  )
                }
                disabled={addedIngredients}
              >
                <Text style={styles.addButtonText}>
                  {addedIngredients
                    ? "✓ Generated Recipe Saved!"
                    : "Save Generated Recipe"}
                </Text>
              </Pressable>
            </View>
          ) : null}
          <Pressable
            style={[styles.previewBtn, { marginTop: 8 }]}
            onPress={() => {
              setUri(null);
              setAnalysisResult(null);
              setAddedIngredients(false);
              setExpandedRecipe(null);
            }}
          >
            <Text style={styles.previewBtnText}>📷 Take Another</Text>
          </Pressable>
        </ScrollView>
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
  budgetSummaryCard: {
    marginTop: 8,
    padding: 14,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.04)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    gap: 10,
  },
  budgetSummaryTitle: {
    color: ACCENT,
    fontWeight: "700",
    fontSize: 14,
  },
  budgetSummaryStatus: {
    color: "#fff",
    fontSize: 13,
    fontWeight: "600",
  },
  budgetSummaryRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
  },
  budgetSummaryLabel: { color: "#888", fontSize: 13 },
  budgetSummaryValue: { color: "#fff", fontSize: 13, fontWeight: "600" },
  budgetSummaryPrompt: { color: "#ccc", fontSize: 12, lineHeight: 18 },
  budgetSummaryHint: { color: ACCENT, fontSize: 12, lineHeight: 18 },
  recipeCard: {
    backgroundColor: "rgba(255,255,255,0.04)",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    marginTop: 8,
    overflow: "hidden",
  },
  recipeHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 14,
  },
  recipeName: { color: "#fff", fontSize: 14, fontWeight: "600" },
  recipeCategory: { color: "#555", fontSize: 12, marginTop: 2 },
  recipeScore: { color: ACCENT, fontSize: 14, fontWeight: "bold" },
  recipeDetails: {
    padding: 14,
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
  useRecipeBtn: {
    marginTop: 16,
    backgroundColor: ACCENT,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  useRecipeBtnText: {
    color: "#000",
    fontWeight: "bold",
    fontSize: 14,
  },
});
