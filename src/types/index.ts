export interface User {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  ranch_name?: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  location?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  status: 'active' | 'resolved';
  created_at: string;
  updated_at: string;
  created_by: string;
  ranch_name?: string;
}

export interface LivestockRequest {
  id: string;
  user_id: string;
  user_name: string;
  ranch_name: string;
  request_type: 'evacuation' | 'shelter' | 'feed' | 'medical' | 'other';
  description: string;
  location?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface LoginCredentials {
  identifier: string; // email or phone
  password: string;
}

export interface RegisterData {
  name: string;
  email?: string;
  phone?: string;
  ranch_name?: string;
  password: string;
  confirm_password: string;
}

export interface CreateUserData {
  name: string;
  email?: string;
  phone?: string;
  ranch_name?: string;
  password: string;
  is_admin: boolean;
}

export interface UpdateUserData {
  name?: string;
  email?: string;
  phone?: string;
  ranch_name?: string;
  is_admin?: boolean;
}

export interface CreateAlertData {
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  location?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

export interface UpdateAlertData {
  title?: string;
  description?: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  location?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  status?: 'active' | 'resolved';
}

export interface NotificationData {
  title: string;
  body: string;
  data?: Record<string, any>;
  sound?: string;
  badge?: number;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy?: number;
  timestamp?: number;
}

export interface AppConfig {
  apiUrl: string;
  firebaseConfig: {
    apiKey: string;
    authDomain: string;
    projectId: string;
    storageBucket: string;
    messagingSenderId: string;
    appId: string;
    vapidKey: string;
  };
  version: string;
  buildNumber: string;
}

export interface TabBadge {
  [key: string]: number | undefined;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

export interface AlertState {
  alerts: Alert[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export interface AppState {
  isOnline: boolean;
  isLoading: boolean;
  error: string | null;
  notifications: NotificationData[];
  location: LocationData | null;
} 