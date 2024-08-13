import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { AuthService } from './auth.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'news_sphere';
  isAuthRoute: boolean = false;
  isDashboardRoute: boolean = false;
  isArticlesRoute: boolean = false;
  isBookmarksRoute: boolean = false;
  isCategoryRoute: boolean = false; // Added this property
  isAuthenticated: boolean = false;
  isArticleDetailRoute: boolean = false;

  constructor(private router: Router, private authService: AuthService) {}

  ngOnInit() {
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      const url = event.urlAfterRedirects;

      // Update route indicators
      this.isAuthRoute = this.isAuthRouteUrl(url);
      this.isDashboardRoute = this.isDashboardRouteUrl(url);
      this.isArticlesRoute = this.isArticlesRouteUrl(url);
      this.isBookmarksRoute = this.isBookmarksRouteUrl(url);
      this.isArticleDetailRoute = this.isArticleDetailRouteUrl(url);
      this.isCategoryRoute = this.isCategoryRouteUrl(url); // Update the category route check

      // Check authentication status
      this.isAuthenticated = this.authService.isAuthenticated();

      // Redirect to login if trying to access articles while not authenticated
      if (this.isArticlesRoute && !this.isAuthenticated) {
        this.router.navigate(['/login']);
      }
    });
  }

  private isAuthRouteUrl(url: string): boolean {
    return url === '/login' || url === '/register';
  }

  private isDashboardRouteUrl(url: string): boolean {
    return url === '/dashboard';
  }

  private isArticlesRouteUrl(url: string): boolean {
    return url.startsWith('/articles') && !this.hasQueryParams(url); // Check for articles route and query parameters
  }

  private isBookmarksRouteUrl(url: string): boolean {
    return url === '/bookmarks';
  }

  private isArticleDetailRouteUrl(url: string): boolean {
    return url.startsWith('/article/');
  }

  private isCategoryRouteUrl(url: string): boolean {
    return url.startsWith('/articles/category/') || this.hasQueryParams(url); // Check for category route and query parameters
  }

  private hasQueryParams(url: string): boolean {
    return url.includes('?'); // Check if URL contains query parameters
  }

  logout() {
    this.authService.logout().subscribe({
      next: () => {
        this.isAuthenticated = false;
        // Navigation is handled in AuthService
      },
      error: (error: any) => {
        console.error('Logout error:', error);
        // Handle error, if any
      }
    });
  }
}
