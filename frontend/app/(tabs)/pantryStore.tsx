type PantryItem = {
  id: string;
  type: string;
  data: string;
  addedAt: string;
};

type SavedRecipe = {
  id: string;
  name: string;
  ingredients: string[];
  instructions: string;
  savedAt: string;
};

let items: PantryItem[] = [];
let savedRecipes: SavedRecipe[] = [];
const listeners: (() => void)[] = [];

export const pantryStore = {
  getItems: () => items,
  addItem: (type: string, data: string) => {
    items = [
      {
        id: Date.now().toString(),
        type,
        data,
        addedAt: new Date().toLocaleString(),
      },
      ...items,
    ];
    listeners.forEach((l) => l());
  },
  removeItem: (id: string) => {
    items = items.filter((i) => i.id !== id);
    listeners.forEach((l) => l());
  },

  // Saved recipes
  getSavedRecipes: () => savedRecipes,
  saveRecipe: (name: string, ingredients: string[], instructions: string) => {
    const existing = savedRecipes.find((r) => r.name === name);
    if (existing) return; // no duplicate
    savedRecipes = [
      {
        id: Date.now().toString(),
        name,
        ingredients,
        instructions,
        savedAt: new Date().toLocaleString(),
      },
      ...savedRecipes,
    ];
    listeners.forEach((l) => l());
  },
  removeRecipe: (id: string) => {
    savedRecipes = savedRecipes.filter((r) => r.id !== id);
    listeners.forEach((l) => l());
  },

  subscribe: (fn: () => void) => {
    listeners.push(fn);
    return () => {
      const idx = listeners.indexOf(fn);
      if (idx > -1) listeners.splice(idx, 1);
    };
  },
};
