import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Button } from 'react-native-paper';
import { colors, spacing, typography } from '../theme';

export default function LivestockScreen() {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.title}>Livestock Management</Text>
          <Text style={styles.subtitle}>
            Request assistance for your livestock during emergencies
          </Text>
          
          <View style={styles.buttonContainer}>
            <Button
              mode="contained"
              icon="car"
              style={styles.button}
              onPress={() => {/* Navigate to evacuation request */}}
            >
              Evacuation Request
            </Button>
            
            <Button
              mode="contained"
              icon="home"
              style={styles.button}
              onPress={() => {/* Navigate to shelter request */}}
            >
              Shelter Request
            </Button>
            
            <Button
              mode="contained"
              icon="food"
              style={styles.button}
              onPress={() => {/* Navigate to feed request */}}
            >
              Feed Request
            </Button>
            
            <Button
              mode="contained"
              icon="medical-bag"
              style={styles.button}
              onPress={() => {/* Navigate to medical request */}}
            >
              Medical Request
            </Button>
          </View>
        </Card.Content>
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundPrimary,
    padding: spacing.md,
  },
  card: {
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    marginBottom: spacing.xl,
  },
  buttonContainer: {
    gap: spacing.md,
  },
  button: {
    marginBottom: spacing.sm,
  },
}); 