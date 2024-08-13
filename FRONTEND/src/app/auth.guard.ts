import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { CanActivateFn } from '@angular/router';

export const authGuard: CanActivateFn = async () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Check if the user is authenticated
  const isAuthenticated = await authService.isAuthenticated(); // Assuming this is async

  if (isAuthenticated) {
    return true;
  } else {
    // Redirect to login if not authenticated
    await router.navigate(['/login']);
    return false;
  }
};
