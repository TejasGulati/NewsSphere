import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent {

  constructor(private authService: AuthService, private router: Router) {}

  logout(): void {
    this.authService.logout().subscribe({
      next: () => {
        // Navigation is handled in AuthService
      },
      error: (error: any) => {
        console.error('Error logging out:', error);
      }
    });
  }

  navigateToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }
}