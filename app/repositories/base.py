# app/repositories/base.py
from __future__ import annotations

from typing import Protocol, Optional, runtime_checkable
from app.models import User, RefreshToken, EmailVerification, PasswordReset


@runtime_checkable
class UserRepo(Protocol):
    """Interfaccia del repository utenti."""

    def find_by_email(self, email: str) -> Optional[User]:
        """Ritorna l'utente con quella email, oppure None se non esiste."""
        ...

    def find_by_id(self, user_id: str) -> Optional[User]:
        """Ritorna l'utente per id, oppure None se non esiste."""
        ...

    def save(self, u: User) -> User:
        """Inserisce/aggiorna l'utente e ritorna l'istanza persistita (refresh fatta)."""
        ...

    def set_password(self, u: User, password_hash: str) -> None:
        """Aggiorna l'hash della password per l'utente dato e commit."""
        ...

    def disable(self, u: User) -> None:
        """Imposta is_active=False e commit."""
        ...


@runtime_checkable
class RefreshRepo(Protocol):
    """Interfaccia del repository per refresh token."""

    def get(self, jti: str) -> Optional[RefreshToken]:
        """Ritorna il refresh token per jti, oppure None."""
        ...

    def save(self, rt: RefreshToken) -> None:
        """Inserisce un nuovo refresh token e commit."""
        ...

    def revoke(self, jti: str) -> None:
        """Marca come revocato il refresh con jti (se esiste) e commit."""
        ...

    def revoke_all(self, user_id: str) -> int:
        """Revoca tutti i refresh attivi dell'utente; ritorna il numero di record toccati."""
        ...


@runtime_checkable
class VerifyRepo(Protocol):
    """Interfaccia del repository per token di verifica email."""

    def create(self, ev: EmailVerification) -> None:
        """Inserisce un nuovo token di verifica e commit."""
        ...

    def get(self, token: str) -> Optional[EmailVerification]:
        """Ritorna il token di verifica, oppure None."""
        ...

    def consume(self, token: str) -> None:
        """Segna il token di verifica come consumato e commit."""
        ...


@runtime_checkable
class ResetRepo(Protocol):
    """Interfaccia del repository per token di reset password."""

    def create(self, pr: PasswordReset) -> None:
        """Inserisce un nuovo token di reset e commit."""
        ...

    def get(self, token: str) -> Optional[PasswordReset]:
        """Ritorna il token di reset, oppure None."""
        ...

    def consume(self, token: str) -> None:
        """Segna il token di reset come consumato e commit."""
        ...
