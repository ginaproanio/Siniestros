import { useState } from 'react';

export interface UseFormSavingOptions {
  onSave: () => Promise<void>;
  onSuccess?: (message: string) => void;
  onError?: (error: string) => void;
  successMessage?: string;
}

export interface UseFormSavingReturn {
  isSaving: boolean;
  save: () => Promise<void>;
  lastError: string | null;
  clearError: () => void;
}

/**
 * Hook reutilizable para manejo de guardado de formularios
 * Elimina duplicación de lógica de loading, error handling y success feedback
 */
export const useFormSaving = (options: UseFormSavingOptions): UseFormSavingReturn => {
  const { onSave, onSuccess, onError, successMessage } = options;
  const [isSaving, setIsSaving] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  const save = async () => {
    if (isSaving) return; // Prevenir múltiples saves simultáneos

    setIsSaving(true);
    setLastError(null);

    try {
      await onSave();

      // Llamar callback de éxito si existe
      if (onSuccess) {
        onSuccess(successMessage || 'Guardado exitosamente');
      }
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail ||
                          error?.response?.data?.message ||
                          error?.message ||
                          'Error desconocido al guardar';

      setLastError(errorMessage);

      // Llamar callback de error si existe
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setIsSaving(false);
    }
  };

  const clearError = () => {
    setLastError(null);
  };

  return {
    isSaving,
    save,
    lastError,
    clearError,
  };
};
