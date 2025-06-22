import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Card,
  HelperText,
  Divider,
} from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import { colors, spacing, typography } from '../theme';

export default function LoginScreen() {
  const { login, register, error, isLoading, clearError } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    identifier: '', // email or phone
    password: '',
    confirmPassword: '',
    ranchName: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!isLogin) {
      if (!formData.name.trim()) {
        newErrors.name = 'Name is required';
      }
      if (!formData.ranchName.trim()) {
        newErrors.ranchName = 'Ranch name is required';
      }
    }

    if (!formData.identifier.trim()) {
      newErrors.identifier = 'Email or phone is required';
    } else if (!isValidEmail(formData.identifier) && !isValidPhone(formData.identifier)) {
      newErrors.identifier = 'Please enter a valid email or phone number';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (!isLogin && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const isValidPhone = (phone: string) => {
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    clearError();

    try {
      if (isLogin) {
        await login({
          identifier: formData.identifier,
          password: formData.password,
        });
      } else {
        await register({
          name: formData.name,
          email: isValidEmail(formData.identifier) ? formData.identifier : undefined,
          phone: isValidPhone(formData.identifier) ? formData.identifier : undefined,
          ranch_name: formData.ranchName,
          password: formData.password,
          confirm_password: formData.confirmPassword,
        });
      }
    } catch (error) {
      Alert.alert('Error', 'An unexpected error occurred. Please try again.');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      identifier: '',
      password: '',
      confirmPassword: '',
      ranchName: '',
    });
    setErrors({});
    clearError();
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    resetForm();
  };

  return (
    <LinearGradient colors={colors.primaryGradient} style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.header}>
            <Text style={styles.logo}>🔥</Text>
            <Text style={styles.title}>Ranch Fire Alert</Text>
            <Text style={styles.subtitle}>
              {isLogin ? 'Sign in to your account' : 'Create your account'}
            </Text>
          </View>

          <Card style={styles.card}>
            <Card.Content style={styles.cardContent}>
              {!isLogin && (
                <>
                  <TextInput
                    label="Full Name"
                    value={formData.name}
                    onChangeText={(text) => setFormData({ ...formData, name: text })}
                    mode="outlined"
                    style={styles.input}
                    error={!!errors.name}
                    disabled={isLoading}
                  />
                  <HelperText type="error" visible={!!errors.name}>
                    {errors.name}
                  </HelperText>

                  <TextInput
                    label="Ranch Name"
                    value={formData.ranchName}
                    onChangeText={(text) => setFormData({ ...formData, ranchName: text })}
                    mode="outlined"
                    style={styles.input}
                    error={!!errors.ranchName}
                    disabled={isLoading}
                  />
                  <HelperText type="error" visible={!!errors.ranchName}>
                    {errors.ranchName}
                  </HelperText>
                </>
              )}

              <TextInput
                label="Email or Phone"
                value={formData.identifier}
                onChangeText={(text) => setFormData({ ...formData, identifier: text })}
                mode="outlined"
                style={styles.input}
                error={!!errors.identifier}
                disabled={isLoading}
                keyboardType="email-address"
                autoCapitalize="none"
              />
              <HelperText type="error" visible={!!errors.identifier}>
                {errors.identifier}
              </HelperText>

              <TextInput
                label="Password"
                value={formData.password}
                onChangeText={(text) => setFormData({ ...formData, password: text })}
                mode="outlined"
                style={styles.input}
                error={!!errors.password}
                disabled={isLoading}
                secureTextEntry
              />
              <HelperText type="error" visible={!!errors.password}>
                {errors.password}
              </HelperText>

              {!isLogin && (
                <>
                  <TextInput
                    label="Confirm Password"
                    value={formData.confirmPassword}
                    onChangeText={(text) => setFormData({ ...formData, confirmPassword: text })}
                    mode="outlined"
                    style={styles.input}
                    error={!!errors.confirmPassword}
                    disabled={isLoading}
                    secureTextEntry
                  />
                  <HelperText type="error" visible={!!errors.confirmPassword}>
                    {errors.confirmPassword}
                  </HelperText>
                </>
              )}

              {error && (
                <HelperText type="error" visible={true}>
                  {error}
                </HelperText>
              )}

              <Button
                mode="contained"
                onPress={handleSubmit}
                style={styles.button}
                loading={isLoading}
                disabled={isLoading}
              >
                {isLogin ? 'Sign In' : 'Create Account'}
              </Button>
            </Card.Content>
          </Card>

          <View style={styles.footer}>
            <Divider style={styles.divider} />
            <Button
              mode="text"
              onPress={toggleMode}
              disabled={isLoading}
              style={styles.toggleButton}
            >
              {isLogin
                ? "Don't have an account? Sign up"
                : 'Already have an account? Sign in'}
            </Button>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  logo: {
    fontSize: 60,
    marginBottom: spacing.md,
  },
  title: {
    ...typography.h1,
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
  },
  card: {
    marginBottom: spacing.lg,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  cardContent: {
    padding: spacing.lg,
  },
  input: {
    marginBottom: spacing.sm,
  },
  button: {
    marginTop: spacing.md,
    paddingVertical: spacing.sm,
  },
  footer: {
    alignItems: 'center',
  },
  divider: {
    width: '100%',
    marginBottom: spacing.md,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  toggleButton: {
    marginTop: spacing.sm,
  },
}); 