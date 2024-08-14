import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable, combineLatest, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { DashboardService } from '../dashboard.service';

interface User {
  id: number;
  name: string;
}

interface Article {
  id: number;
  title: string;
  summary: string;
  media_url?: string;
  content?: string;
  category?: string;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  user: User = { id: 0, name: '' };
  welcomeMessage = 'Welcome to your personalized news dashboard!';
  articles: Article[] = [];
  recommendedArticles: Article[] = [];
  trendingArticles: Article[] = [];
  categories: string[] = ['Technology', 'Politics', 'Sports', 'Entertainment', 'Science'];
  userStats = {
    articlesRead: 0,
    bookmarks: 0
  };

  private userUrl = 'http://127.0.0.1:8000/users/user'; // Updated URL
  private articlesUrl = 'http://127.0.0.1:8000/dashboard/articles'; // Adjust as needed
  private recommendedArticlesUrl = 'http://127.0.0.1:8000/dashboard/articles/recommended';
  private trendingArticlesUrl = 'http://127.0.0.1:8000/dashboard/articles/trending';
  private bookmarksUrl = 'http://127.0.0.1:8000/dashboard/bookmarks/count';
  private viewsUrl = 'http://127.0.0.1:8000/dashboard/articles/view-count';

  constructor(
    private http: HttpClient, 
    private router: Router,
    private dashboardService: DashboardService
  ) {}

  ngOnInit(): void {
    combineLatest([
      this.loadUserDetails(),
      this.loadArticles(),
      this.loadRecommendedArticles(),
      this.loadTrendingArticles(),
      this.loadUserStats()
    ]).subscribe({
      next: ([user, articles, recommendedArticles, trendingArticles, userStats]) => {
        this.user = user;
        this.articles = articles;
        this.recommendedArticles = recommendedArticles;
        this.trendingArticles = trendingArticles;
        this.userStats = userStats;
      },
      error: (error) => {
        console.error('Error loading data:', error);
      }
    });
  }

  private loadUserDetails(): Observable<User> {
    return this.http.get<User>(this.userUrl).pipe(
      catchError(error => {
        console.error('Error fetching user details:', error);
        return of({ id: 0, name: 'Guest' }); // Return a default user object
      })
    );
  }

  private loadArticles(): Observable<Article[]> {
    return this.http.get<Article[]>(this.articlesUrl).pipe(
      catchError(error => {
        console.error('Error fetching articles:', error);
        return of([]); // Return an empty array
      })
    );
  }

  private loadRecommendedArticles(): Observable<Article[]> {
    return this.http.get<Article[]>(this.recommendedArticlesUrl).pipe(
      catchError(error => {
        console.error('Error fetching recommended articles:', error);
        return of([]); // Return an empty array
      })
    );
  }

  private loadTrendingArticles(): Observable<Article[]> {
    return this.http.get<Article[]>(this.trendingArticlesUrl).pipe(
      catchError(error => {
        console.error('Error fetching trending articles:', error);
        return of([]); // Return an empty array
      })
    );
  }

  private loadUserStats(): Observable<any> {
    return combineLatest([
      this.getBookmarksCount(),
      this.getViewsCount()
    ]).pipe(
      map(([bookmarks, views]) => ({
        bookmarks,
        articlesRead: views
      })),
      catchError(error => {
        console.error('Error fetching user stats:', error);
        return of({ bookmarks: 0, articlesRead: 0 }); // Return default stats
      })
    );
  }

  private getBookmarksCount(): Observable<number> {
    return this.http.get<{ bookmark_count: number }>(this.bookmarksUrl).pipe(
      map(response => response.bookmark_count),
      catchError(error => {
        console.error('Error fetching bookmarks count:', error);
        return of(0); // Return default count
      })
    );
  }

  private getViewsCount(): Observable<number> {
    return this.http.get<{ view_count: number }>(this.viewsUrl).pipe(
      map(response => response.view_count),
      catchError(error => {
        console.error('Error fetching views count:', error);
        return of(0); // Return default count
      })
    );
  }

  filterByCategory(category: string): void {
    console.log(`Filtering by category: ${category}`);
    this.dashboardService.setSelectedCategory(category.toLowerCase());
    this.router.navigate(['/articles'], { queryParams: { category: category.toLowerCase() } });
  }

  readArticle(articleId: number): void {
    console.log(`Reading article with id: ${articleId}`);
    this.router.navigate(['/article', articleId]);
  }
}