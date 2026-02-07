# CloakAI Frontend (Next.js)

This is the frontend repository for the CloakAI privacy protection system, built with **Next.js**.

---

## Features

- **Next.js App Router**: Optimized performance and routing.
- **Upload Interface**: Drag-and-drop secure file upload.
- **Privacy Controls**: Selectable protection modes (`low`, `mid`, `high`).
- **Real-time Status**: Live progress tracking and status updates via API polling.
- **Secure Download**: Retrieval of processed, cloaked images.

---

## Tech Stack

- **Next.js 16+**
- **React 19**
- **Axios**: API communication
- **CSS**: Custom styling with responsive design

---

## Quick Start

### Prerequisites

- Node.js (v18+) // Updated for Next.js

### Installation

```bash
npm install
```

### Configuration

Create a `.env.local` file in the root:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run Locally

```bash
npm run dev
```

- App runs at: [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

---

## Deployment (Vercel)

1. Connect your repository to Vercel.
2. Vercel automatically detects Next.js.
3. Add the `NEXT_PUBLIC_API_URL` environment variable in the Vercel project settings (pointing to your running backend API).
4. Deploy.

### Common Issues

- **Missing Root Directory**: Ensures your **Root Directory** in Vercel settings is set to `./` (empty), not `frontend`.
- **Wrong Branch**: Ensure the **Production Branch** is set to `frontend`, not `main`.

---

## License

BSD-3-Clause
