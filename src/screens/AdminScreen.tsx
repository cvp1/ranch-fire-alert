import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Button } from 'react-native-paper';
import { colors, spacing, typography } from '../theme';

export default function AdminScreen() {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.title}>Admin Panel</Text>
          <Text style={styles.subtitle}>
            Manage users, alerts, and system settings
          </Text>
          
          <View style={styles.buttonContainer}>
            <Button
              mode="contained"
              icon="account-multiple"
              style={styles.button}
              onPress={() => {/* Navigate to user management */}}
            >
              User Management
            </Button>
            
            <Button
              mode="contained"
              icon="alert"
              style={styles.button}
              onPress={() => {/* Navigate to alert management */}}
            >
              Alert Management
            </Button>
            
            <Button
              mode="contained"
              icon="chart-line"
              style={styles.button}
              onPress={() => {/* Navigate to analytics */}}
            >
              Analytics
            </Button>
            
            <Button
              mode="contained"
              icon="cog"
              style={styles.button}
              onPress={() => {/* Navigate to system settings */}}
            >
              System Settings
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