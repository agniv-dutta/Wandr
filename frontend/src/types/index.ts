export interface TripFormData {
  destination: string;
  duration: number;
  budgetAmount: number;
  budgetCurrency: string;
  budgetLevel: 'Budget' | 'Moderate' | 'Luxury';
  travelStyle: string;
  constraints: string;
}

export interface WeatherDay {
  date: string;
  condition: string;
  maxTemp: number;
  minTemp: number;
  precipitation: number;
  windSpeed: number;
  weatherCode: number;
}

export interface AgentStep {
  tool: string;
  input: string;
  output: string;
}

export interface TripResult {
  finalAnswer: string;
  intermediateSteps: AgentStep[];
  destination: string;
  duration: number;
}

export interface DestinationInfo {
  country: string;
  capital: string;
  population: string;
  timezone: string;
  currency: string;
  languages: string[];
  coordinates: {
    latitude: number;
    longitude: number;
  };
  tips: string[];
}

export interface CurrencyConversion {
  converted: number;
  rate: number;
  updated: string;
  from: string;
  to: string;
  amount: number;
}

export interface WeatherForecast {
  forecast: WeatherDay[];
  recommendation: string;
}
