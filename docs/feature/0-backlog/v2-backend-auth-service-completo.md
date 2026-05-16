# Feature: v2-backend-auth-service-completo

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar auth service completo: register, login, logout, refresh token, password hash

## Tipo
- [ ] Frontend
- [x] Backend
- [ ] Ambos

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como sistema, necesito un servicio de autenticación completo y seguro para validar usuarios.

---

## Criterios de Aceptación
- [ ] Register con hash de password usando bcrypt
- [ ] Login que valide credenciales y devuelva JWT
- [ ] Logout que invalide sesión
- [ ] Password con hash pbkdf2 (compatible con V1)
- [ ] JWT con expiry configurado
- [ ] Refresh token endpoint
- [ ] Tests unitarios para auth service

---

## Tasks
- [ ] Implementar hash_password() con bcrypt
- [ ] Implementar verify_password()
- [ ] Implementar create_access_token() con jose
- [ ] Implementar AuthService.register()
- [ ] Implementar AuthService.login()
- [ ] Implementar AuthService.logout()
- [ ] Crear /api/auth/register endpoint
- [ ] Escribir tests para auth service

---

## Notas Técnicas
V1 usa pbkdf2_sha256 con 160_000 iteraciones - mantener compatibilidad.
FastAPI usa python-jose para JWT.
Ver security.py existente en v2/backend/app/core/