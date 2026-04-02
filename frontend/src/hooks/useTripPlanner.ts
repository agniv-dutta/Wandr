import { useState, useCallback } from 'react';
import { TripFormData, TripResult } from '../types';
import { travelApi } from '../api/travel';

export interface UseTripPlannerState {
  result: TripResult | null;
  isLoading: boolean;
  error: string | null;
}

export interface UseTripPlannerActions {
  planTrip: (formData: TripFormData) => Promise<void>;
  reset: () => void;
  clearError: () => void;
}

export const useTripPlanner = (): UseTripPlannerState & UseTripPlannerActions => {
  const [result, setResult] = useState<TripResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const planTrip = useCallback(async (formData: TripFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const tripResult = await travelApi.planTrip(formData);
      setResult(tripResult);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to plan trip';
      setError(errorMessage);
      console.error('Trip planning error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setIsLoading(false);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    result,
    isLoading,
    error,
    planTrip,
    reset,
    clearError,
  };
};
