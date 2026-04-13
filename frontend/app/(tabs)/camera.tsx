import { CameraType, CameraView, useCameraPermissions } from "expo-camera";
import { useRef, useState, useEffect } from "react";
import { budgetStore, BUDGET_TIERS, BudgetTier } from "./budgetStore";
import {
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
  Animated,
  Modal,
  Button,
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
  const [scanned, setScanned] = useState(false);
  const [scanMode, setScanMode] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [budgetTier, setBudgetTier] = useState<BudgetTier | null>(null);
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [scanResult, setScanResult] = useState<{
    type: string;
    data: string;
  } | null>(null);
  const [added, setAdded] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [addedIngredients, setAddedIngredients] = useState(false);
  const [lastAnalysisTier, setLastAnalysisTier] = useState<BudgetTier | null>(
    null,
  );
  const [analysisResult, setAnalysisResult] = useState<{
    ingredients: { name: string; category: string }[];
    matched_recipes: { name: string; match_score: { percentage: number } }[];
    generated_recipe?: string | null;
    generated_recipe_pricing?: {
      estimatedTotal?: number;
      subtotal?: number;
      pricedCount?: number;
      requestedCount?: number;
    } | null;
    generated_recipe_pricing_ingredients?: string[];
    generated_recipe_pricing_error?: string | null;
    recipe_generation_error?: string | null;
    recipe_over_budget?: boolean;
    can_regenerate?: boolean;
    regeneration_prompt?: string | null;
    regeneration_requested?: boolean;
  } | null>(null);

  const sweepAnim = useRef(new Animated.Value(0)).current;
  const slideUp = useRef(new Animated.Value(300)).current;

  useEffect(() => {
    if (scanMode && !scanned) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(sweepAnim, {
            toValue: 1,
            duration: 1800,
            useNativeDriver: true,
          }),
          Animated.timing(sweepAnim, {
            toValue: 0,
            duration: 1800,
            useNativeDriver: true,
          }),
        ]),
      ).start();
    } else {
      sweepAnim.stopAnimation();
      sweepAnim.setValue(0);
    }
  }, [scanMode, scanned]);

  useEffect(() => {
    budgetStore.load().then((t) => {
      if (t) setBudgetTier(t);
    });
  }, []);

  useEffect(() => {
    if (scanResult) {
      Animated.spring(slideUp, {
        toValue: 0,
        useNativeDriver: true,
        tension: 80,
        friction: 12,
      }).start();
    } else {
      slideUp.setValue(300);
    }
  }, [scanResult]);

  useEffect(() => {
    if (!analysisResult || !uri || !lastAnalysisTier) return;
    if (!analysisResult.can_regenerate || analysisResult.regeneration_requested)
      return;

    Alert.alert(
      "Recipe outside budget range",
      analysisResult.regeneration_prompt ||
        "This recipe is outside your selected budget range. Regenerate recipe?",
      [
        { text: "No", style: "cancel" },
        {
          text: "Yes",
          onPress: () =>
            analyzeImage(uri, lastAnalysisTier, {
              regenerateRecipe: true,
            }),
        },
      ],
      { cancelable: true },
    );
  }, [analysisResult, uri, lastAnalysisTier]);

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

  const handleBarcodeScanned = ({
    type,
    data,
  }: {
    type: string;
    data: string;
  }) => {
    if (scanned) return;
    setScanned(true);
    setScanResult({ type, data });
    setAdded(false);
  };

  const handleAddToPantry = () => {
    if (!scanResult || added) return;
    pantryStore.addItem(scanResult.type, scanResult.data);
    setAdded(true);
  };

  const handleScanAgain = () => {
    setScanResult(null);
    setAdded(false);
    setScanMode(false);
    setTimeout(() => {
      setScanMode(true);
      setScanned(false);
    }, 300);
  };

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
    options?: { regenerateRecipe?: boolean },
  ) => {
    setAnalyzing(true);
    setLastAnalysisTier(tier);
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

      const res = await fetch("http://192.168.1.166:5001/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image: base64,
          budget_tier: tier,
          regenerate_recipe: Boolean(options?.regenerateRecipe),
        }),
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setAnalysisResult(data);
    } catch (e: any) {
      alert("Analysis failed: " + e.message);
    } finally {
      setAnalyzing(false);
    }
  };

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
          <ScrollView
            style={styles.analysisScroll}
            contentContainerStyle={styles.analysisScrollContent}
            showsVerticalScrollIndicator={false}
          >
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

            <Text style={styles.analysisTitle}>👩‍🍳 Generated Recipe</Text>
            {analysisResult.generated_recipe ? (
              <View style={styles.generatedRecipeBox}>
                <Text style={styles.generatedRecipeText}>
                  {analysisResult.generated_recipe}
                </Text>
              </View>
            ) : (
              <Text style={styles.analysisNone}>
                {analysisResult.recipe_generation_error
                  ? `Could not generate recipe: ${analysisResult.recipe_generation_error}`
                  : "No generated recipe returned"}
              </Text>
            )}

            <Text style={styles.analysisTitle}>💲 Estimated Recipe Cost</Text>
            {analysisResult.generated_recipe_pricing ? (
              <View style={styles.priceCard}>
                <Text style={styles.priceValue}>
                  $
                  {Number(
                    analysisResult.generated_recipe_pricing.estimatedTotal ??
                      analysisResult.generated_recipe_pricing.subtotal ??
                      0,
                  ).toFixed(2)}
                </Text>
                <Text style={styles.priceMeta}>
                  {analysisResult.generated_recipe_pricing.pricedCount ?? 0} of{" "}
                  {analysisResult.generated_recipe_pricing.requestedCount ?? 0}{" "}
                  ingredients priced
                </Text>
                {analysisResult.generated_recipe_pricing_ingredients?.length ? (
                  <Text style={styles.priceIngredients}>
                    Used:{" "}
                    {analysisResult.generated_recipe_pricing_ingredients.join(
                      ", ",
                    )}
                  </Text>
                ) : null}
              </View>
            ) : (
              <Text style={styles.analysisNone}>
                {analysisResult.generated_recipe_pricing_error
                  ? `Could not price recipe: ${analysisResult.generated_recipe_pricing_error}`
                  : "No pricing returned"}
              </Text>
            )}
          </ScrollView>

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

  const renderCamera = () => {
    const sweepTranslate = sweepAnim.interpolate({
      inputRange: [0, 1],
      outputRange: [-120, 120],
    });

    return (
      <View style={styles.cameraContainer}>
        <CameraView
          style={styles.camera}
          ref={ref}
          facing={facing}
          responsiveOrientationWhenOrientationLocked
          onBarcodeScanned={
            scanMode && !scanned ? handleBarcodeScanned : undefined
          }
          barcodeScannerSettings={{
            barcodeTypes: [
              "qr",
              "ean13",
              "ean8",
              "upc_a",
              "upc_e",
              "code39",
              "code128",
              "pdf417",
              "aztec",
              "datamatrix",
            ],
          }}
        />

        <Pressable style={styles.menuBtn} onPress={() => setMenuOpen(true)}>
          <Text style={styles.menuBtnText}>•••</Text>
        </Pressable>

        {scanMode && (
          <View style={styles.scanOverlay}>
            <View style={styles.scanBox}>
              <View style={[styles.corner, styles.topLeft]} />
              <View style={[styles.corner, styles.topRight]} />
              <View style={[styles.corner, styles.bottomLeft]} />
              <View style={[styles.corner, styles.bottomRight]} />
              {!scanned && (
                <Animated.View
                  style={[
                    styles.sweepLine,
                    { transform: [{ translateY: sweepTranslate }] },
                  ]}
                />
              )}
            </View>
            <Text style={styles.scanText}>Align barcode within the box</Text>
            <Pressable
              style={styles.cancelScanBtn}
              onPress={() => {
                setScanMode(false);
                setScanned(false);
                setScanResult(null);
              }}
            >
              <Text style={styles.cancelScanText}>✕ Cancel Scan</Text>
            </Pressable>
          </View>
        )}

        {!scanMode && (
          <View style={styles.shutterContainer}>
            <Pressable onPress={toggleFacing}>
              <FontAwesome6 name="rotate-left" size={28} color="white" />
            </Pressable>
            <Pressable onPress={takePicture}>
              {({ pressed }) => (
                <View
                  style={[styles.shutterBtn, { opacity: pressed ? 0.5 : 1 }]}
                >
                  <View style={styles.shutterBtnInner} />
                </View>
              )}
            </Pressable>
            <View style={{ width: 28 }} />
          </View>
        )}

        {scanResult && (
          <Animated.View
            style={[
              styles.resultCard,
              { transform: [{ translateY: slideUp }] },
            ]}
          >
            <View style={styles.resultHandle} />
            <Text style={styles.resultTitle}>✅ Barcode Scanned!</Text>
            <View style={styles.resultRow}>
              <Text style={styles.resultLabel}>Type</Text>
              <Text style={styles.resultValue}>{scanResult.type}</Text>
            </View>
            <View style={styles.resultRow}>
              <Text style={styles.resultLabel}>Data</Text>
              <Text style={styles.resultValue} numberOfLines={2}>
                {scanResult.data}
              </Text>
            </View>
            <View style={styles.resultButtons}>
              <Pressable
                style={[styles.addButton, added && styles.addButtonDone]}
                onPress={handleAddToPantry}
              >
                <Text style={styles.addButtonText}>
                  {added ? "✓ Added!" : "Add to Pantry"}
                </Text>
              </Pressable>
              <Pressable
                style={styles.scanAgainButton}
                onPress={handleScanAgain}
              >
                <Text style={styles.scanAgainText}>Scan Again</Text>
              </Pressable>
            </View>
          </Animated.View>
        )}

        <Modal
          transparent
          visible={menuOpen}
          animationType="fade"
          onRequestClose={() => setMenuOpen(false)}
        >
          <Pressable
            style={styles.modalOverlay}
            onPress={() => setMenuOpen(false)}
          >
            <View style={styles.menuDropdown}>
              <Text style={styles.menuHeader}>Options</Text>
              <Pressable
                style={styles.menuItem}
                onPress={() => {
                  setMenuOpen(false);
                  setScanMode(true);
                  setScanned(false);
                  setScanResult(null);
                }}
              >
                <Text style={styles.menuItemIcon}>▦</Text>
                <Text style={styles.menuItemText}>Scan Barcode</Text>
              </Pressable>
            </View>
          </Pressable>
        </Modal>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {uri ? renderPicture(uri) : renderCamera()}
    </View>
  );
}

const CORNER_SIZE = 24;
const CORNER_THICKNESS = 3;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
    alignItems: "center",
    justifyContent: "center",
  },
  cameraContainer: StyleSheet.absoluteFillObject,
  camera: StyleSheet.absoluteFillObject,
  menuBtn: {
    position: "absolute",
    top: 52,
    right: 20,
    backgroundColor: "rgba(0,0,0,0.5)",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.15)",
  },
  menuBtnText: { color: "#fff", fontSize: 16, letterSpacing: 2 },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.4)" },
  menuDropdown: {
    position: "absolute",
    top: 90,
    right: 16,
    backgroundColor: "#1a1a2e",
    borderRadius: 14,
    padding: 8,
    minWidth: 180,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
  },
  menuHeader: {
    color: "#555",
    fontSize: 11,
    fontWeight: "600",
    letterSpacing: 1,
    paddingHorizontal: 12,
    paddingVertical: 6,
    textTransform: "uppercase",
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderRadius: 10,
    gap: 10,
  },
  menuItemIcon: { fontSize: 18, color: ACCENT },
  menuItemText: { color: "#fff", fontSize: 15, fontWeight: "500" },
  scanOverlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: "center",
    justifyContent: "center",
  },
  scanBox: {
    width: 250,
    height: 250,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },
  corner: {
    position: "absolute",
    width: CORNER_SIZE,
    height: CORNER_SIZE,
    borderColor: ACCENT,
  },
  topLeft: {
    top: 0,
    left: 0,
    borderTopWidth: CORNER_THICKNESS,
    borderLeftWidth: CORNER_THICKNESS,
  },
  topRight: {
    top: 0,
    right: 0,
    borderTopWidth: CORNER_THICKNESS,
    borderRightWidth: CORNER_THICKNESS,
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    borderBottomWidth: CORNER_THICKNESS,
    borderLeftWidth: CORNER_THICKNESS,
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    borderBottomWidth: CORNER_THICKNESS,
    borderRightWidth: CORNER_THICKNESS,
  },
  sweepLine: {
    position: "absolute",
    width: "100%",
    height: 2,
    backgroundColor: ACCENT,
    opacity: 0.8,
  },
  scanText: {
    color: "white",
    marginTop: 16,
    fontSize: 13,
    backgroundColor: "rgba(0,0,0,0.55)",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    overflow: "hidden",
  },
  cancelScanBtn: {
    marginTop: 20,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: "rgba(255,255,255,0.1)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.2)",
  },
  cancelScanText: { color: "#fff", fontSize: 14 },
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
    justifyContent: "flex-start",
    gap: 12,
    paddingTop: 20,
    paddingBottom: 16,
  },
  previewImage: {
    width: "100%",
    height: 240,
    flexShrink: 0,
  },
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
  resultCard: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "#1a1a2e",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40,
  },
  resultHandle: {
    width: 40,
    height: 4,
    backgroundColor: "#444",
    borderRadius: 2,
    alignSelf: "center",
    marginBottom: 16,
  },
  resultTitle: {
    color: ACCENT,
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 16,
  },
  resultRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#2a2a3e",
  },
  resultLabel: { color: "#888", fontSize: 14 },
  resultValue: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "600",
    maxWidth: "70%",
    textAlign: "right",
  },
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
  scanAgainButton: {
    flex: 1,
    backgroundColor: "rgba(255,255,255,0.08)",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#333",
  },
  scanAgainText: { color: "#fff", fontWeight: "bold", fontSize: 15 },
  analysisCard: {
    width: "100%",
    backgroundColor: "#1a1a2e",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    gap: 8,
    maxHeight: 520,
    flexShrink: 1,
  },
  analysisScroll: {
    flexGrow: 0,
  },
  analysisScrollContent: {
    gap: 8,
    paddingBottom: 12,
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
  generatedRecipeBox: {
    backgroundColor: "rgba(255,255,255,0.04)",
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    padding: 14,
  },
  generatedRecipeText: {
    color: "#eee",
    fontSize: 13,
    lineHeight: 20,
  },
  priceCard: {
    backgroundColor: "rgba(74,222,128,0.08)",
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "rgba(74,222,128,0.22)",
    padding: 14,
    gap: 6,
  },
  priceValue: {
    color: "#fff",
    fontSize: 26,
    fontWeight: "800",
  },
  priceMeta: {
    color: "#9be7b5",
    fontSize: 12,
  },
  priceIngredients: {
    color: "#cfeedd",
    fontSize: 12,
    lineHeight: 18,
  },

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
  budgetModalTitle: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "bold",
  },
  budgetModalSubtitle: {
    color: "#555",
    fontSize: 13,
    marginBottom: 8,
  },
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
  budgetOptionLabel: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 15,
  },
  budgetOptionDesc: {
    color: "#888",
    fontSize: 13,
  },
  budgetOptionCheck: {
    color: ACCENT,
    fontSize: 18,
    fontWeight: "bold",
  },
});
