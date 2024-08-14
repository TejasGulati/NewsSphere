import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { Router } from '@angular/router';

// Define interfaces for API responses
interface LoginResponse {
  access: string;
  refresh: string;
}

interface RegisterResponse {
  // Define fields as per your backend response
}

interface ErrorResponse {
  error: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8000/users'; // Use environment variable if needed
  private loggedIn = new BehaviorSubject<boolean>(this.isAuthenticated());

  constructor(private http: HttpClient, private router: Router) {}

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login/`, { email, password }).pipe(
      tap(response => {
        this.storeTokens(response);
        this.loggedIn.next(true);
      }),
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'An unknown error occurred!';
        if (error.error) {
          if (typeof error.error === 'string') {
            errorMessage = error.error;
          } else if (error.error.email) {
            errorMessage = error.error.email[0];
          } else if (error.error.password) {
            errorMessage = error.error.password[0];
          } else {
            errorMessage = Object.values(error.error).flat().join(' ');
          }
        }
        return throwError(() => new Error(errorMessage));
      })
    );
  }

  register(name: string, email: string, password: string): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.apiUrl}/register/`, { name, email, password }).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'An unknown error occurred!';
        if (error.error) {
          if (typeof error.error === 'string') {
            errorMessage = error.error;
          } else if (error.error.email) {
            errorMessage = error.error.email[0];
          } else if (error.error.password) {
            errorMessage = error.error.password[0];
          } else {
            errorMessage = Object.values(error.error).flat().join(' ');
          }
        }
        return throwError(() => new Error(errorMessage));
      })
    );
  }

  logout(): Observable<void> {
    return new Observable<void>(observer => {
      this.clearTokens();
      this.loggedIn.next(false);
      this.router.navigate(['/login']);
      observer.next();
      observer.complete();
    });
  }

  getToken(): string | null {
    return localStorage.getItem('accessToken');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  refreshToken(): Observable<LoginResponse> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      return throwError(() => new Error('Refresh token not available'));
    }

    return this.http.post<LoginResponse>(`${this.apiUrl}/refresh/`, {}, {
      headers: new HttpHeaders({ 'Authorization': `Bearer ${refreshToken}` })
    }).pipe(
      tap(response => {
        this.storeTokens(response);
      }),
      catchError(error => {
        this.logout();
        return throwError(() => error);
      })
    );
  }

  getLoggedInStatus(): Observable<boolean> {
    return this.loggedIn.asObservable();
  }

  private storeTokens(response: LoginResponse): void {
    localStorage.setItem('accessToken', response.access);
    localStorage.setItem('refreshToken', response.refresh);
  }

  private clearTokens(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  private handleError(error: any): Observable<never> {
    let errorMessage = 'An unknown error occurred!';
    if (error.error instanceof ErrorEvent) {
      // Client-side or network error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Backend error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}