import { CameraType, CameraView, useCameraPermissions } from "expo-camera";
import { useRef, useState, useEffect } from "react";
import {
  Button,
  Pressable,
  StyleSheet,
  Text,
  View,
  Animated,
} from "react-native";
import { Image } from "expo-image";
import FontAwesome6 from "@expo/vector-icons/FontAwesome6";
import { pantryStore } from "./pantryStore";

const ACCENT = "#4ade80";

export default function Camera() {
  const [permission, requestPermission] = useCameraPermissions();
  const ref = useRef<CameraView>(null);
  const [uri, setUri] = useState<string | null>(null);
  const [facing, setFacing] = useState<CameraType>("back");
  const [scanned, setScanned] = useState(false);
  const [scanMode, setScanMode] = useState(false);
  const [scanResult, setScanResult] = useState<{
    type: string;
    data: string;
  } | null>(null);
  const [added, setAdded] = useState(false);

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

  const renderPicture = (uri: string) => (
    <View>
      <Image
        source={{ uri }}
        contentFit="contain"
        style={{ width: 500, aspectRatio: 1 }}
      />
      <Button onPress={() => setUri(null)} title="Take another picture" />
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
          </View>
        )}

        <View style={styles.shutterContainer}>
          <Pressable
            onPress={() => {
              setScanMode(!scanMode);
              setScanned(false);
              setScanResult(null);
              setAdded(false);
            }}
          >
            <View
              style={[styles.scanButton, scanMode && styles.scanButtonActive]}
            >
              <Text
                style={[
                  styles.scanButtonText,
                  scanMode && styles.scanButtonTextActive,
                ]}
              >
                {scanMode ? "Stop Scan" : "Scan Barcode"}
              </Text>
            </View>
          </Pressable>
          {!scanMode && (
            <Pressable onPress={takePicture}>
              {({ pressed }) => (
                <View
                  style={[styles.shutterBtn, { opacity: pressed ? 0.5 : 1 }]}
                >
                  <View style={styles.shutterBtnInner} />
                </View>
              )}
            </Pressable>
          )}
          <Pressable onPress={toggleFacing}>
            <FontAwesome6 name="rotate-left" size={32} color="white" />
          </Pressable>
        </View>

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
    shadowColor: ACCENT,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 1,
    shadowRadius: 6,
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
  scanButton: {
    backgroundColor: "rgba(0,0,0,0.6)",
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "white",
  },
  scanButtonActive: {
    backgroundColor: "rgba(74,222,128,0.15)",
    borderColor: ACCENT,
  },
  scanButtonText: {
    color: "white",
    fontWeight: "bold",
  },
  scanButtonTextActive: {
    color: ACCENT,
  },
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
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
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
  resultLabel: {
    color: "#888",
    fontSize: 14,
  },
  resultValue: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "600",
    maxWidth: "70%",
    textAlign: "right",
  },
  resultButtons: {
    flexDirection: "row",
    gap: 12,
    marginTop: 20,
  },
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
  addButtonText: {
    color: "#000",
    fontWeight: "bold",
    fontSize: 15,
  },
  scanAgainButton: {
    flex: 1,
    backgroundColor: "rgba(255,255,255,0.08)",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#333",
  },
  scanAgainText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 15,
  },
});
