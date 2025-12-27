import { useState } from 'react';
import { Search } from 'lucide-react';
import { ChemicalSearchService } from './services/ChemicalSearchService';
import type { ChemicalSummary, Chemical } from './types';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ChemicalSummary[]>([]);
  const [selectedChemical, setSelectedChemical] = useState<Chemical | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await ChemicalSearchService.search(query);
      setResults(data.items);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectChemical = async (id: number) => {
    setLoading(true);
    try {
      const chemical = await ChemicalSearchService.getChemical(id);
      setSelectedChemical(chemical);
    } catch (error) {
      console.error('Failed to load chemical:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">CAMEO Chemicals</h1>
          <p className="text-gray-600">Offline Chemical Database</p>
        </header>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search chemicals by name or synonym..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2"
            >
              <Search size={20} />
              Search
            </button>
          </form>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-4">
              <h2 className="text-xl font-semibold mb-4">Results ({results.length})</h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {results.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleSelectChemical(item.id)}
                    className="w-full text-left p-3 rounded hover:bg-blue-50 border border-gray-200 transition-colors"
                  >
                    <div className="font-medium text-gray-900">{item.name}</div>
                    {item.synonyms && (
                      <div className="text-sm text-gray-500 truncate">{item.synonyms}</div>
                    )}
                  </button>
                ))}
                {results.length === 0 && !loading && (
                  <p className="text-gray-500 text-center py-4">No results</p>
                )}
              </div>
            </div>
          </div>

          <div className="md:col-span-2">
            {selectedChemical ? (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-4">{selectedChemical.name}</h2>
                
                {selectedChemical.description && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2">Description</h3>
                    <p className="text-gray-700">{selectedChemical.description}</p>
                  </div>
                )}

                {selectedChemical.health_haz && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2">Health Hazards</h3>
                    <p className="text-gray-700">{selectedChemical.health_haz}</p>
                  </div>
                )}

                {selectedChemical.fire_haz && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2">Fire Hazards</h3>
                    <p className="text-gray-700">{selectedChemical.fire_haz}</p>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t">
                  {selectedChemical.nfpa_health !== null && (
                    <div>
                      <span className="font-semibold">NFPA Health:</span> {selectedChemical.nfpa_health}
                    </div>
                  )}
                  {selectedChemical.nfpa_flam !== null && (
                    <div>
                      <span className="font-semibold">NFPA Flammability:</span> {selectedChemical.nfpa_flam}
                    </div>
                  )}
                  {selectedChemical.nfpa_react !== null && (
                    <div>
                      <span className="font-semibold">NFPA Reactivity:</span> {selectedChemical.nfpa_react}
                    </div>
                  )}
                  {selectedChemical.molwgt_value !== null && (
                    <div>
                      <span className="font-semibold">Molecular Weight:</span> {selectedChemical.molwgt_value}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-500">
                Select a chemical from the results to view details
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
