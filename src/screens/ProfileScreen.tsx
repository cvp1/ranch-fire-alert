import React from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Text, Card, Button, Avatar, Divider } from 'react-native-paper';
import { useAuth } from '../context/AuthContext';
import { colors, spacing, typography } from '../theme';

export default function ProfileScreen() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Sign Out', style: 'destructive', onPress: logout },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <Card style={styles.profileCard}>
        <Card.Content style={styles.profileContent}>
          <Avatar.Text 
            size={80} 
            label={user?.name?.charAt(0) || 'U'} 
            style={styles.avatar}
          />
          <Text style={styles.name}>{user?.name || 'User'}</Text>
          <Text style={styles.email}>{user?.email || user?.phone || 'No contact info'}</Text>
          <Text style={styles.ranch}>{user?.ranch_name || 'No ranch specified'}</Text>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.sectionTitle}>Account Settings</Text>
          
          <Button
            mode="outlined"
            icon="account-edit"
            style={styles.button}
            onPress={() => {/* Navigate to edit profile */}}
          >
            Edit Profile
          </Button>
          
          <Button
            mode="outlined"
            icon="bell"
            style={styles.button}
            onPress={() => {/* Navigate to notification settings */}}
          >
            Notification Settings
          </Button>
          
          <Button
            mode="outlined"
            icon="map-marker"
            style={styles.button}
            onPress={() => {/* Navigate to location settings */}}
          >
            Location Settings
          </Button>
          
          <Divider style={styles.divider} />
          
          <Button
            mode="outlined"
            icon="help-circle"
            style={styles.button}
            onPress={() => {/* Navigate to help */}}
          >
            Help & Support
          </Button>
          
          <Button
            mode="outlined"
            icon="information"
            style={styles.button}
            onPress={() => {/* Navigate to about */}}
          >
            About App
          </Button>
          
          <Divider style={styles.divider} />
          
          <Button
            mode="outlined"
            icon="logout"
            style={[styles.button, styles.logoutButton]}
            onPress={handleLogout}
            textColor={colors.error}
          >
            Sign Out
          </Button>
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
  profileCard: {
    marginBottom: spacing.lg,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  profileContent: {
    alignItems: 'center',
    padding: spacing.xl,
  },
  avatar: {
    marginBottom: spacing.md,
    backgroundColor: colors.primary,
  },
  name: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  email: {
    ...typography.body1,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  ranch: {
    ...typography.body2,
    color: colors.textTertiary,
  },
  card: {
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  sectionTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  button: {
    marginBottom: spacing.sm,
  },
  divider: {
    marginVertical: spacing.md,
  },
  logoutButton: {
    borderColor: colors.error,
  },
}); 