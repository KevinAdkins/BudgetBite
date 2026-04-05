import AsyncStorage from "@react-native-async-storage/async-storage";

export type BudgetTier = "tier1" | "tier2" | "tier3";

export const BUDGET_TIERS = {
  tier1: {
    label: "Tier 1 - Cheapest",
    description: "Less than $25",
    value: "tier1",
  },
  tier2: {
    label: "Tier 2 - Middle",
    description: "$25 to $50",
    value: "tier2",
  },
  tier3: {
    label: "Tier 3 - Expensive",
    description: "Greater than $50",
    value: "tier3",
  },
};

const KEY = "budgetbite_budget_tier";

export const budgetStore = {
  save: async (tier: BudgetTier) => {
    await AsyncStorage.setItem(KEY, tier);
  },
  load: async (): Promise<BudgetTier | null> => {
    const val = await AsyncStorage.getItem(KEY);
    return (val as BudgetTier) || null;
  },
};
