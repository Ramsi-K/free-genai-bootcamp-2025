# HagXwon - Korean Language Learning Platform

HagXwon is a modern, futuristic Korean language learning platform featuring a sleek, high-tech UI with glassmorphism, neon elements, and dynamic transitions. The application helps users learn Korean through various practice modes including word practice, listening comprehension, and sentence construction.

![HagXwon Platform](https://example.com/images/hagxwon-preview.png)

## Features

- **Futuristic UI/UX**: Sleek, high-tech design with glassmorphism, neon effects, and dynamic transitions
- **Word Practice**: Learn vocabulary filtered by TOPIK level or most common words
- **Listening Practice**: Improve comprehension by listening to Korean audio
- **Sentence Practice**: Build Korean sentences and test your knowledge
- **VectorDB Integration**: Semantic search for related words (placeholder implementation)
- **LLM Integration**: Advanced word suggestions powered by large language models (placeholder implementation)
- **Study History**: Comprehensive tracking of your learning progress
- **Admin Controls**: Manage application data and reset options

## Technologies

- **React 18** with TypeScript
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Router** for navigation
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 16.x or higher
- npm or yarn

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/hagxwon.git
cd hagxwon
```

2. Install dependencies

```bash
npm install
# or
yarn install
```

3. Start the development server

```bash
npm run dev
# or
yarn dev
```

4. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```text
hagxwon/
├── public/                  # Static assets
├── src/
│   ├── components/          # React components
│   │   ├── HagXwonLogo.tsx  # Brand logo component
│   │   ├── Navbar.tsx       # Navigation component
│   │   └── ui/              # Reusable UI components
│   ├── hooks/               # Custom React hooks
│   ├── pages/               # Page components
│   ├── services/            # API services
│   ├── store/               # Zustand state management
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── styles/              # Global styles
│   ├── App.tsx              # Main App component
│   └── main.tsx             # Entry point
├── .eslintrc.json           # ESLint configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── vite.config.ts           # Vite configuration
```

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the app for production
- `npm run preview` - Preview the production build locally
- `npm run lint` - Run ESLint
- `npm test` - Run unit and integration tests
- `npm run test:e2e` - Run end-to-end tests
- `npm run coverage` - Generate test coverage report

## Testing Architecture

### Mock Backend

- MSW (Mock Service Worker) for API request interception
- Simulated network conditions and errors
- localStorage persistence
- Complete coverage of API endpoints

### Test Coverage

1. **Unit Tests**

   - Utility functions
   - Custom hooks (useStudySession, useLocalStorage, useVectorDB)
   - Zustand stores
   - Data formatting utilities

2. **Component Tests**

   - WordPractice workflow
   - ListeningPractice audio simulation
   - SentencePractice interactions
   - Dashboard rendering
   - Theme switching
   - Responsive design tests

3. **Integration Tests**
   - Complete practice session flows
   - Practice type switching
   - Semantic search functionality
   - Study history management

### Test Structure

```text
src/
├── __tests__/
│   ├── components/     # Component tests
│   ├── integration/    # Integration tests
│   └── unit/          # Unit tests
├── mocks/             # MSW handlers
├── fixtures/          # Test data
└── setupTests.ts      # Test configuration
```

## OPEA Integration

The application is designed to integrate with OPEA megaservices:

- **Word Service**: Retrieves Korean vocabulary and definitions
- **Audio Service**: Provides text-to-speech for pronunciation
- **VectorDB**: Enables semantic search for related words
- **LLM Integration**: Powers intelligent word suggestions

Currently, these services are implemented as placeholders and can be connected to your actual OPEA megaservice backend.

## Backend Connection

To connect to your backend services:

1. Update the API base URL in `src/services/api.ts`
2. Implement the actual API calls in the service files
3. Configure authentication if required

## Design System

HagXwon features a comprehensive design system with:

- **Color Palette**: Primary blue (#4A90E2) and purple (#6B2FB3) gradients
- **Typography**: Modern, clean typography optimized for language learning
- **Components**: Glassmorphism cards, neon effects, futuristic buttons
- **Animations**: Smooth transitions, floating elements, and scanning effects

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Korean language content is provided for educational purposes
- Icon library by [Lucide](https://lucide.dev/)
- Inspired by modern language learning applications and futuristic UI designs
