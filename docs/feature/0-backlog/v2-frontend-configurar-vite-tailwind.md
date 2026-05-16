# Feature: v2-frontend-configurar-vite-tailwind

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Configurar Vite con React, TypeScript strict mode y Tailwind CSS v4 en el frontend V2

## Tipo
- [x] Frontend
- [ ] Backend
- [ ] Ambos

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como desarrollador, quiero un entorno de build moderno con TypeScript y Tailwind para poder construir componentes tipados y con estilos consistentes.

---

## Criterios de Aceptación
- [ ] Vite configurado con React y TypeScript
- [ ] tsconfig.json con strict mode
- [ ] Tailwind CSS v4 instalado y configurado
- [ ] Path alias @/* funcionando
- [ ] Componente de prueba renderiza correctamente
- [ ] `npm run dev` levanta sin errores
- [ ] `npm run build` genera build válida

---

## Tasks
- [ ] Actualizar package.json con dependencias de React, TypeScript, Tailwind, Vite
- [ ] Crear tsconfig.json con strict mode
- [ ] Crear vite.config.ts
- [ ] Configurar Tailwind CSS v4
- [ ] Configurar path alias @/*
- [ ] Crear App.tsx de prueba
- [ ] Verificar que build funciona

---

## Notas Técnicas
Verificar que las dependencias en package.json sean las últimas versiones compatibles.
Tailwind v4 tiene cambios significativos respecto a v3 - verificar sintaxis.