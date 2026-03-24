type PantryItem = {
  id: string;
  type: string;
  data: string;
  addedAt: string;
};

let items: PantryItem[] = [];
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
  subscribe: (fn: () => void) => {
    listeners.push(fn);
    return () => {
      const idx = listeners.indexOf(fn);
      if (idx > -1) listeners.splice(idx, 1);
    };
  },
};
