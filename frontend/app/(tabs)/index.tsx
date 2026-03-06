import { Text, View, StyleSheet } from "react-native";
import { Link } from "expo-router";

export default function Index() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Hello World</Text>
      <Link href="/pantry" style={styles.button}>
        Go to Pantry Screen
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#25292e",
    alignItems: "center",
    justifyContent: "center",
  },
  text : {
    fontSize: 20,
    fontWeight: "bold",
    color: "#fff",
  },
  button: {
    marginTop: 20,
    padding: 10,
    backgroundColor: "#61dafb",
    borderRadius: 5,
  },
});
