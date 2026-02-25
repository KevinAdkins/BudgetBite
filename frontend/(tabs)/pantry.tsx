import { Text, View, StyleSheet } from "react-native";

export default function PantryScreen() {
    return (
        <View style={styles.container}>
            <Text style={styles.text}>This is the Pantry Screen</Text>
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
    text: {
        fontSize: 20,
        fontWeight: "bold",
        color: "#fff",
    },
});