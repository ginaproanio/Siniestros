import { useState } from 'react';

export interface TabConfig {
  id: number;
  title: string;
  icon?: string;
  completed?: boolean;
}

export interface UseTabNavigationReturn {
  activeTab: number;
  completedTabs: number[];
  goToTab: (tabId: number) => void;
  nextTab: () => void;
  previousTab: () => void;
  markTabCompleted: (tabId: number) => void;
  isTabCompleted: (tabId: number) => boolean;
  canGoNext: boolean;
  canGoPrevious: boolean;
  progress: number;
}

/**
 * Hook reutilizable para navegación por pestañas con estado de completitud
 * Elimina duplicación entre SiniestroForm e InvestigacionForm
 */
export const useTabNavigation = (
  tabs: TabConfig[],
  initialTab: number = 0
): UseTabNavigationReturn => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [completedTabs, setCompletedTabs] = useState<number[]>([]);

  const goToTab = (tabId: number) => {
    if (tabId >= 0 && tabId < tabs.length) {
      setActiveTab(tabId);
    }
  };

  const nextTab = () => {
    if (activeTab < tabs.length - 1) {
      // Marcar tab actual como completado si no está ya completado
      setCompletedTabs(prev => {
        if (!prev.includes(activeTab)) {
          return [...prev, activeTab];
        }
        return prev;
      });
      setActiveTab(activeTab + 1);
    }
  };

  const previousTab = () => {
    if (activeTab > 0) {
      setActiveTab(activeTab - 1);
    }
  };

  const markTabCompleted = (tabId: number) => {
    setCompletedTabs(prev => {
      if (!prev.includes(tabId)) {
        return [...prev, tabId];
      }
      return prev;
    });
  };

  const isTabCompleted = (tabId: number) => {
    return completedTabs.includes(tabId);
  };

  const canGoNext = activeTab < tabs.length - 1;
  const canGoPrevious = activeTab > 0;
  const progress = ((completedTabs.length + (isTabCompleted(activeTab) ? 1 : 0)) / tabs.length) * 100;

  return {
    activeTab,
    completedTabs,
    goToTab,
    nextTab,
    previousTab,
    markTabCompleted,
    isTabCompleted,
    canGoNext,
    canGoPrevious,
    progress,
  };
};
