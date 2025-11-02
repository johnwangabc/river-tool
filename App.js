import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import SettingsScreen from './src/screens/SettingsScreen';
import ActivityScreen from './src/screens/ActivityScreen';
import RiverPatrolScreen from './src/screens/RiverPatrolScreen';
import ComprehensiveScreen from './src/screens/ComprehensiveScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <PaperProvider>
      <NavigationContainer>
        <StatusBar style="auto" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName;

              if (route.name === 'Settings') {
                iconName = focused ? 'cog' : 'cog-outline';
              } else if (route.name === 'Activity') {
                iconName = focused ? 'calendar-check' : 'calendar-check-outline';
              } else if (route.name === 'RiverPatrol') {
                iconName = focused ? 'water' : 'water-outline';
              } else if (route.name === 'Comprehensive') {
                iconName = focused ? 'chart-bar' : 'chart-bar-outline';
              }

              return <Icon name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#6200ee',
            tabBarInactiveTintColor: 'gray',
            headerStyle: {
              backgroundColor: '#6200ee',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          })}
        >
          <Tab.Screen
            name="Activity"
            component={ActivityScreen}
            options={{
              title: '活动统计',
              headerTitle: '活动数据统计',
            }}
          />
          <Tab.Screen
            name="RiverPatrol"
            component={RiverPatrolScreen}
            options={{
              title: '巡护评测',
              headerTitle: '河流巡护/评测',
            }}
          />
          <Tab.Screen
            name="Comprehensive"
            component={ComprehensiveScreen}
            options={{
              title: '综合统计',
              headerTitle: '综合次数统计',
            }}
          />
          <Tab.Screen
            name="Settings"
            component={SettingsScreen}
            options={{
              title: '设置',
              headerTitle: '应用设置',
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
}
