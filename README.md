# CloakAI Frontend

This is the frontend repository for the CloakAI privacy protection system. It is a React Single Page Application (SPA).

---

## Features

- **Upload Interface**: Drag-and-drop secure file upload.
- **Privacy Controls**: Selectable protection modes (`low`, `mid`, `high`).
- **Real-time Status**: Live progress tracking and status updates via API polling.
- **Secure Download**: Retrieval of processed, cloaked images.

---

## Tech Stack

- **React**: UI library
- **Axios**: API communication
- **CSS**: Custom styling with responsive design

---

## Quick Start

### Prerequisites

- Node.js (v14+)
- npm

### Installation

```bash
npm install
```

### Configuration

Create a `.env` file in the root (or set environment variables in your deployment platform):

```env
REACT_APP_API_URL=http://localhost:8000
```

### Run Locally

```bash
npm start
```

- App runs at: [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
```

---

## Deployment (Vercel)

This project is configured for Vercel.

1. Connect your repository to Vercel.
2. Vercel should auto-detect "Create React App".
3. Add the `REACT_APP_API_URL` environment variable in the Vercel project settings (pointing to your running backend API).
4. Deploy.

A `vercel.json` file is included to handle client-side routing.

---

## License

BSD-3-Clause
