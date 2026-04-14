import { Text, View, StyleSheet, StatusBar } from "react-native";
import { Link } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";

export default function Index() {
  return (
    <LinearGradient
      colors={["#0f0c29", "#1a1a40", "#0d0d1a"]}
      style={styles.container}
      start={{ x: 0.2, y: 0 }}
      end={{ x: 0.8, y: 1 }}
    >
      <StatusBar barStyle="light-content" />
      <View style={styles.logoArea}>
        <Text style={styles.logoEmoji}>🛒</Text>
        <Text style={styles.logoText}>BudgetBite</Text>
        <Text style={styles.tagline}>Smart shopping, simplified.</Text>
      </View>
      <View style={styles.cardArea}>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Get Started</Text>
          <Text style={styles.cardSubtext}>
            Scan or type in food items to track your pantry in real time.
          </Text>
          <Link href="/camera" style={styles.button}>
            <Text style={styles.buttonText}>📷 Start Scanning</Text>
          </Link>
          <Link href="/pantry" style={styles.outlineButton}>
            <Text style={styles.outlineButtonText}>🧊 View Pantry</Text>
          </Link>
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "space-between",
    paddingVertical: 60,
  },
  logoArea: {
    alignItems: "center",
    paddingTop: 40,
    gap: 8,
  },
  logoEmoji: {
    fontSize: 56,
  },
  logoText: {
    fontSize: 36,
    fontWeight: "800",
    color: "#fff",
    letterSpacing: 1,
  },
  tagline: {
    fontSize: 14,
    color: "#888",
    letterSpacing: 0.5,
  },
  cardArea: {
    paddingHorizontal: 24,
  },
  card: {
    backgroundColor: "rgba(255,255,255,0.05)",
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    gap: 12,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#fff",
    marginBottom: 4,
  },
  cardSubtext: {
    fontSize: 14,
    color: "#888",
    marginBottom: 8,
    lineHeight: 20,
  },
  button: {
    backgroundColor: "#4ade80",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    textAlign: "center",
    color: "#000",
    fontWeight: "700",
    fontSize: 15,
    overflow: "hidden",
    paddingHorizontal: 20,
  },
  buttonText: {
    color: "#000",
    fontWeight: "700",
    fontSize: 15,
    textAlign: "center",
  },
  outlineButton: {
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    textAlign: "center",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.15)",
    paddingHorizontal: 20,
  },
  outlineButtonText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 15,
    textAlign: "center",
  },
});
