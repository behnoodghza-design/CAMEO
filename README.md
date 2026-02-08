# CAMEO Chemicals - Chemical Reactivity Analysis Platform

A professional Flask + React web application for analyzing chemical compatibility and reactivity based on NOAA CAMEO data.

## 🏗️ Project Structure

```
CAMEO-new/
├── backend/                    # Flask backend application
│   ├── app.py                 # Main Flask application
│   ├── data/                  # Active database (DO NOT MODIFY)
│   │   └── chemicals.db       # Primary chemical database
│   ├── logic/                 # Core business logic
│   │   ├── reactivity_engine.py  # Chemical compatibility engine
│   │   ├── constants.py       # Compatibility enums and mappings
│   │   └── __init__.py
│   ├── templates/             # Jinja2 HTML templates
│   │   ├── base.html          # Base template
│   │   ├── mixer.html         # Chemical mixer UI
│   │   └── chemical_detail.html  # Chemical detail page with NFPA
│   ├── scripts/               # Backend utility scripts
│   │   └── ensure_data.py     # Database verification & patching
│   ├── tests/                 # Backend unit tests
│   │   └── matrix_stress_test.py
│   └── requirements.txt       # Python dependencies
│
├── src/                       # React frontend (Vite + TypeScript)
│   ├── App.tsx               # Main React component
│   ├── main.tsx              # Entry point
│   ├── index.css             # Global styles
│   ├── services/             # API services
│   │   └── ChemicalSearchService.ts
│   └── types/                # TypeScript type definitions
│
├── scripts/                   # Utility scripts for data management
│   ├── map_pdfs.py           # Map PDFs to database records
│   ├── extract_pdf_data.py   # Extract data from PDF files
│   ├── audit_mapping.py      # Audit PDF mappings
│   ├── fix_carbon.py         # Fix carbon reactivity rules
│   ├── fix_water_group.py    # Fix water group assignments
│   └── verify_pdf_usage.py   # Verify PDF integration
│
├── tests/                     # Integration tests
│   ├── test_comprehensive.py # Comprehensive test suite
│   ├── test_migration.py     # Migration tests
│   └── verify_water.py       # Water reactivity verification
│
├── resources/                 # Secondary resources
│   └── chemicals.db          # Secondary DB (used by utility scripts)
│
├── PDF_Folder/               # PDF library (1500+ files)
│   ├── Material/             # Material safety data sheets
│   └── Guides/               # Emergency response guides
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md       # System architecture
│   └── LOGIC.md              # Business logic documentation
│
├── agent_memory/             # AI agent memory system
│   ├── README.md
│   ├── project_structure.json
│   ├── api_registry.json
│   ├── database_schema.json
│   └── history/
│
└── [Config Files]            # Vite, TypeScript, Tailwind configs
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── package.json
    └── index.html
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend runs on `http://localhost:5000`

### Frontend Setup
```bash
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`

## 🔑 Key Features

- **Chemical Search**: Search 1800+ chemicals by name or synonym
- **Reactivity Analysis**: Analyze compatibility between multiple chemicals
- **NFPA 704 Diamond**: Visual hazard display with special codes
- **PDF Integration**: Direct links to NOAA CAMEO material safety data
- **Favorites System**: Save frequently used chemicals
- **Safety-Critical**: Fail-safe design with comprehensive validation

## 📊 Database

- **Primary DB**: `backend/data/chemicals.db` (used by Flask app)
- **Secondary DB**: `resources/chemicals.db` (used by utility scripts)
- **Schema**: See `agent_memory/database_schema.json`

⚠️ **CRITICAL**: Never modify database content directly. Use provided scripts.

## 🧪 Testing

```bash
# Backend tests
python backend/tests/matrix_stress_test.py

# Integration tests
python tests/test_comprehensive.py
python tests/verify_water.py
```

## 📚 API Endpoints

See `agent_memory/api_registry.json` for complete API documentation.

Key endpoints:
- `GET /api/search?q={query}` - Search chemicals
- `GET /api/chemical/{id}` - Get chemical details
- `POST /api/analyze` - Analyze chemical compatibility
- `GET /chemical/{id}` - Render chemical detail page

## 🛠️ Utility Scripts

Located in `scripts/` directory:
- `map_pdfs.py` - Map PDF files to database records
- `extract_pdf_data.py` - Extract structured data from PDFs
- `verify_pdf_usage.py` - Verify PDF integration

## 🔒 Safety Notes

This is a **safety-critical system**. All changes must:
1. Preserve database integrity
2. Maintain fail-safe behavior
3. Include comprehensive testing
4. Follow the Agent Memory Protocol (see `agent_memory/README.md`)

## 📖 Documentation

- **Architecture**: `docs/ARCHITECTURE.md`
- **Business Logic**: `docs/LOGIC.md`
- **Agent Memory**: `agent_memory/README.md`

## 🧠 Agent Memory System

This project uses an AI Agent Memory Protocol v3.0 for maintaining consistency across development sessions. See `agent_memory/README.md` for details.

## 📦 Technology Stack

- **Backend**: Flask 3.x, Python 3.x, SQLite
- **Frontend**: React 18, TypeScript, Vite 5, Tailwind CSS
- **UI Components**: Alpine.js (templates), Lucide Icons
- **Testing**: Python unittest, custom test harness

## 🤝 Contributing

Before making changes:
1. Read `agent_memory/README.md`
2. Review `docs/ARCHITECTURE.md`
3. Check recent history in `agent_memory/history/`
4. Follow the Memory Protocol for structural changes

## 📝 License

NOAA CAMEO Data - Public Domain
Application Code - [Your License]

---

**Last Updated**: February 2026
**Version**: 3.1.0
**Status**: Production Ready
