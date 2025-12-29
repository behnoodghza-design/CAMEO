import type { SearchResult, Chemical } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

export class ChemicalSearchService {
  static async search(query: string): Promise<SearchResult> {
    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Search failed');
      return await response.json();
    } catch (error) {
      console.error('Search service error:', error);
      return { items: [], total: 0 };
    }
  }

  static async getChemical(id: number): Promise<Chemical | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/chemical/${id}`);
      if (!response.ok) {
         if (response.status === 404) return null;
         throw new Error('Get chemical failed');
      }
      return await response.json();
    } catch (error) {
      console.error('Get chemical service error:', error);
      return null;
    }
  }

  static async getFavorites(): Promise<any[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/favorites`);
      if (!response.ok) throw new Error('Get favorites failed');
      return await response.json();
    } catch (error) {
      console.error('Get favorites service error:', error);
      return [];
    }
  }

  static async addFavorite(chemicalId: number, note?: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/favorites`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chemicalId, note }),
      });
      if (!response.ok) throw new Error('Add favorite failed');
      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Add favorite service error:', error);
      return false;
    }
  }

  static async removeFavorite(chemicalId: number): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/favorites/${chemicalId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Remove favorite failed');
      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Remove favorite service error:', error);
      return false;
    }
  }
}
