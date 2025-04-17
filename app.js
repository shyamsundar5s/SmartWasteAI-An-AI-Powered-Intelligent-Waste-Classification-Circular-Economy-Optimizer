import React, { useState } from 'react';
import { View, Text, Button, Image, StyleSheet, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);

  const pickImage = async () => {
    // Ask for permission
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permissionResult.granted) {
      alert("Permission to access media library is required!");
      return;
    }

    // Pick an image
    const pickerResult = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!pickerResult.canceled) {
      setImage(pickerResult.uri);
      classifyImage(pickerResult.uri);
    }
  };

  const classifyImage = async (uri) => {
    const formData = new FormData();
    formData.append('file', {
      uri,
      name: 'waste.jpg',
      type: 'image/jpeg',
    });

    try {
      const response = await fetch("http://127.0.0.1:8000/classify/", {
        method: "POST",
        body: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error in classification:", error);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>SmartWasteAI</Text>
      <Button title="Pick an Image" onPress={pickImage} />
      {image && <Image source={{ uri: image }} style={styles.image} />}
      {result && (
        <View style={styles.result}>
          <Text>Category: {result.category}</Text>
          <Text>Confidence: {result.confidence.toFixed(2)}</Text>
          <Text>Suggestion: {result.suggestion}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 20 },
  image: { width: 200, height: 200, marginTop: 20 },
  result: { marginTop: 20, alignItems: 'center' },
});
