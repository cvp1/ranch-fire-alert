import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  RefreshControl,
  Alert,
} from 'react-native';
import {
  Text,
  Card,
  Chip,
  Button,
  FAB,
  Searchbar,
  Menu,
  Divider,
} from 'react-native-paper';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/apiService';
import { Alert as AlertType, ApiResponse } from '../types';
import { colors, spacing, typography } from '../theme';

export default function AlertsScreen() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [filteredAlerts, setFilteredAlerts] = useState<AlertType[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMenuVisible, setFilterMenuVisible] = useState(false);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');

  useEffect(() => {
    loadAlerts();
  }, []);

  useEffect(() => {
    filterAlerts();
  }, [alerts, searchQuery, selectedSeverity]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const response = await apiService.get<ApiResponse<AlertType[]>>('/alerts');
      
      if (response.success && response.data) {
        setAlerts(response.data);
      } else {
        Alert.alert('Error', response.message || 'Failed to load alerts');
      }
    } catch (error) {
      console.error('Error loading alerts:', error);
      Alert.alert('Error', 'Failed to load alerts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAlerts();
    setRefreshing(false);
  };

  const filterAlerts = () => {
    let filtered = alerts;

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(alert =>
        alert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.location?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by severity
    if (selectedSeverity !== 'all') {
      filtered = filtered.filter(alert => alert.severity === selectedSeverity);
    }

    setFilteredAlerts(filtered);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return colors.critical;
      case 'high':
        return colors.high;
      case 'medium':
        return colors.medium;
      case 'low':
        return colors.low;
      default:
        return colors.textSecondary;
    }
  };

  const getSeverityLabel = (severity: string) => {
    return severity.charAt(0).toUpperCase() + severity.slice(1);
  };

  const renderAlertItem = ({ item }: { item: AlertType }) => (
    <Card style={[styles.alertCard, { borderLeftColor: getSeverityColor(item.severity) }]}>
      <Card.Content>
        <View style={styles.alertHeader}>
          <Text style={styles.alertTitle}>{item.title}</Text>
          <Chip
            mode="outlined"
            textStyle={{ color: getSeverityColor(item.severity) }}
            style={[styles.severityChip, { borderColor: getSeverityColor(item.severity) }]}
          >
            {getSeverityLabel(item.severity)}
          </Chip>
        </View>
        
        <Text style={styles.alertDescription}>{item.description}</Text>
        
        {item.location && (
          <Text style={styles.alertLocation}>📍 {item.location}</Text>
        )}
        
        <View style={styles.alertFooter}>
          <Text style={styles.alertTimestamp}>
            {new Date(item.created_at).toLocaleDateString()}
          </Text>
          <Chip
            mode="outlined"
            textStyle={{ color: item.status === 'active' ? colors.error : colors.success }}
            style={[
              styles.statusChip,
              { borderColor: item.status === 'active' ? colors.error : colors.success }
            ]}
          >
            {item.status === 'active' ? 'Active' : 'Resolved'}
          </Chip>
        </View>
      </Card.Content>
    </Card>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyStateIcon}>🔥</Text>
      <Text style={styles.emptyStateTitle}>No Alerts</Text>
      <Text style={styles.emptyStateSubtitle}>
        {searchQuery || selectedSeverity !== 'all'
          ? 'No alerts match your current filters'
          : 'No fire alerts at this time'}
      </Text>
      {(searchQuery || selectedSeverity !== 'all') && (
        <Button
          mode="outlined"
          onPress={() => {
            setSearchQuery('');
            setSelectedSeverity('all');
          }}
          style={styles.clearFiltersButton}
        >
          Clear Filters
        </Button>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Searchbar
          placeholder="Search alerts..."
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.searchbar}
        />
        
        <Menu
          visible={filterMenuVisible}
          onDismiss={() => setFilterMenuVisible(false)}
          anchor={
            <Button
              mode="outlined"
              onPress={() => setFilterMenuVisible(true)}
              icon="filter-variant"
            >
              Filter
            </Button>
          }
        >
          <Menu.Item
            onPress={() => {
              setSelectedSeverity('all');
              setFilterMenuVisible(false);
            }}
            title="All Severities"
            leadingIcon={selectedSeverity === 'all' ? 'check' : undefined}
          />
          <Divider />
          <Menu.Item
            onPress={() => {
              setSelectedSeverity('critical');
              setFilterMenuVisible(false);
            }}
            title="Critical"
            leadingIcon={selectedSeverity === 'critical' ? 'check' : undefined}
          />
          <Menu.Item
            onPress={() => {
              setSelectedSeverity('high');
              setFilterMenuVisible(false);
            }}
            title="High"
            leadingIcon={selectedSeverity === 'high' ? 'check' : undefined}
          />
          <Menu.Item
            onPress={() => {
              setSelectedSeverity('medium');
              setFilterMenuVisible(false);
            }}
            title="Medium"
            leadingIcon={selectedSeverity === 'medium' ? 'check' : undefined}
          />
          <Menu.Item
            onPress={() => {
              setSelectedSeverity('low');
              setFilterMenuVisible(false);
            }}
            title="Low"
            leadingIcon={selectedSeverity === 'low' ? 'check' : undefined}
          />
        </Menu>
      </View>

      <FlatList
        data={filteredAlerts}
        renderItem={renderAlertItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={renderEmptyState}
        showsVerticalScrollIndicator={false}
      />

      {user?.is_admin && (
        <FAB
          icon="plus"
          style={styles.fab}
          onPress={() => {
            // Navigate to create alert screen
            Alert.alert('Create Alert', 'Navigate to create alert screen');
          }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundPrimary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    gap: spacing.sm,
  },
  searchbar: {
    flex: 1,
    elevation: 0,
    backgroundColor: colors.cardBackground,
  },
  listContainer: {
    padding: spacing.md,
    paddingBottom: spacing.xxl,
  },
  alertCard: {
    marginBottom: spacing.md,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  alertTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    flex: 1,
    marginRight: spacing.sm,
  },
  severityChip: {
    alignSelf: 'flex-start',
  },
  alertDescription: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  alertLocation: {
    ...typography.caption,
    color: colors.textTertiary,
    marginBottom: spacing.sm,
  },
  alertFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  alertTimestamp: {
    ...typography.caption,
    color: colors.textTertiary,
  },
  statusChip: {
    alignSelf: 'flex-start',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xxl,
  },
  emptyStateIcon: {
    fontSize: 64,
    marginBottom: spacing.lg,
  },
  emptyStateTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  emptyStateSubtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  clearFiltersButton: {
    marginTop: spacing.md,
  },
  fab: {
    position: 'absolute',
    margin: spacing.lg,
    right: 0,
    bottom: 0,
    backgroundColor: colors.primary,
  },
}); 