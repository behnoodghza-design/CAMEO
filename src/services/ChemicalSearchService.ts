import type { SearchResult, Chemical } from '../types';

export class ChemicalSearchService {
  static async search(query: string): Promise<SearchResult> {
    try {
      return await window.ipcRenderer.invoke('db:search', query);
    } catch (error) {
      console.error('Search service error:', error);
      return { items: [], total: 0 };
    }
  }

  static async getChemical(id: number): Promise<Chemical | null> {
    try {
      return await window.ipcRenderer.invoke('db:get-chemical', id);
    } catch (error) {
      console.error('Get chemical service error:', error);
      return null;
    }
  }

  static async getFavorites(): Promise<any[]> {
    try {
      return await window.ipcRenderer.invoke('db:get-favorites');
    } catch (error) {
      console.error('Get favorites service error:', error);
      return [];
    }
  }

  static async addFavorite(chemicalId: number, note?: string): Promise<boolean> {
    try {
      const result = await window.ipcRenderer.invoke('db:add-favorite', chemicalId, note);
      return result.success;
    } catch (error) {
      console.error('Add favorite service error:', error);
      return false;
    }
  }

  static async removeFavorite(chemicalId: number): Promise<boolean> {
    try {
      const result = await window.ipcRenderer.invoke('db:remove-favorite', chemicalId);
      return result.success;
    } catch (error) {
      console.error('Remove favorite service error:', error);
      return false;
    }
  }
}
