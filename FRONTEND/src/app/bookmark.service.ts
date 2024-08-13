import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AuthService } from './auth.service';

interface BookmarkedArticle {
  id: number;
  article_title: string;
  article_url: string;
  article_id: number;
  article_content: string;
  article_media_url: string;
  created_at: string;
  user: number;
  article: number;
}

@Injectable({
  providedIn: 'root'
})
export class BookmarkService {
  private apiUrl = 'http://127.0.0.1:8000/dashboard/bookmarks/';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    });
  }

  addBookmark(articleId: number): Observable<any> {
    const body = { article_id: articleId };
    return this.http.post<any>(this.apiUrl, body, { headers: this.getHeaders() }).pipe(
      map(response => {
        if (response.message === 'Article already bookmarked') {
          return { alreadyBookmarked: true };
        }
        return response;
      }),
      catchError(this.handleError)
    );
  }

  removeBookmark(articleId: number): Observable<any> {
    const url = `${this.apiUrl}${articleId}/`;
    return this.http.delete<any>(url, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        if (error.status === 404) {
          return throwError(() => new Error('Bookmark not found or already removed'));
        }
        return this.handleError(error);
      })
    );
  }

  getBookmarks(): Observable<BookmarkedArticle[]> {
    return this.http.get<BookmarkedArticle[]>(this.apiUrl, { headers: this.getHeaders() }).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred!';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client-side Error: ${error.error.message}`;
    } else {
      errorMessage = `Server Error: Code ${error.status}\nMessage: ${error.message}`;
      if (error.error && typeof error.error === 'object') {
        errorMessage += `\nDetails: ${JSON.stringify(error.error)}`;
      }
    }
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}