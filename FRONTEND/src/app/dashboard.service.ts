import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';

interface User {
  id: number;
  name: string;
  email: string;
}

interface DashboardData {
  message: string;
  user: User;
}

interface Article {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  author: string | null;
  source_url: string;
  media_url: string;
  category: string;
  expanded: boolean;
}

interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
  article_id?: number;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = 'http://127.0.0.1:8000';
  private selectedCategorySubject = new BehaviorSubject('');
  selectedCategory$ = this.selectedCategorySubject.asObservable();

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    });
  }

  getDashboardData(): Observable<DashboardData> {
    return this.http.get<DashboardData>(`${this.apiUrl}/dashboard/`, { headers: this.getHeaders() }).pipe(
      catchError(this.handleError)
    );
  }

  getArticles(selectedCategory: string = '', page: number = 1): Observable<PaginatedResponse<Article>> {
    let params = new HttpParams()
      .set('page', page.toString());
    
    if (selectedCategory) {
      params = params.set('category', selectedCategory);
    }

    return this.http.get<PaginatedResponse<Article>>(`${this.apiUrl}/dashboard/articles/`, {
      headers: this.getHeaders(),
      params: params
    }).pipe(
      catchError(this.handleError)
    );
  }

  getArticle(id: number): Observable<Article> {
    return this.http.get<Article>(`${this.apiUrl}/dashboard/articles/${id}/`, { headers: this.getHeaders() }).pipe(
      catchError(this.handleError)
    );
  }

  setSelectedCategory(category: string) {
    this.selectedCategorySubject.next(category);
  }

  getNotifications(): Observable<Notification[]> {
    return this.http.get<Notification[]>(`${this.apiUrl}/dashboard/notifications/`, { headers: this.getHeaders() }).pipe(
      catchError(this.handleError)
    );
  }

  

  deleteNotification(notificationId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/dashboard/notifications/${notificationId}/`, { headers: this.getHeaders() }).pipe(
      catchError(this.handleError)
    );
  }
  
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred!';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client-side Error: ${error.error.message}`;
    } else {
      errorMessage = `Server Error: Code ${error.status}\nMessage: ${error.message}`;
    }
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}