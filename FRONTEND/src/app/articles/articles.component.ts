import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { DashboardService } from '../dashboard.service';
import { BookmarkService } from '../bookmark.service';
import { Subscription, of } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';

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

interface BookmarkedArticle {
  id: number;
  article_title: string;
  article_url: string;
  article_id: number;
  article_content: string;
  article_media_url: string | null;
  created_at: string;
  user: number;
}

@Component({
  selector: 'app-articles',
  templateUrl: './articles.component.html',
  styleUrls: ['./articles.component.css']
})
export class ArticlesComponent implements OnInit, OnDestroy {
  displayedArticles: Article[] = [];
  bookmarkedArticleIds: Set<number> = new Set();
  private refreshSubscription: Subscription | undefined;
  private categorySubscription: Subscription | undefined;

  // Pagination properties
  pageSize: number = 9;
  currentPage: number = 1;
  totalPages: number = 0;
  allArticlesBookmarked: boolean = false;
  hasMoreArticles: boolean = true; // Track if there are more articles available

  // Category filter
  categories: string[] = ['technology', 'sports', 'science', 'politics', 'entertainment'];
  selectedCategory: string = '';  // Default to no category

  // Loading state
  isLoading: boolean = false;

  // Bookmark message
  showBookmarkMessage: boolean = false;
  bookmarkMessage: string = '';

  constructor(
    private dashboardService: DashboardService,
    private bookmarkService: BookmarkService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.selectedCategory = params['category'] || ''; // Default to no category if not present
      this.currentPage = 1;
      this.loadBookmarksAndArticles();
    });
  }

  ngOnDestroy(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
    if (this.categorySubscription) {
      this.categorySubscription.unsubscribe();
    }
  }

  loadBookmarksAndArticles(): void {
    this.isLoading = true;
    this.bookmarkService.getBookmarks().pipe(
      catchError(error => {
        console.error('Error loading bookmarks:', error);
        return of([]);
      }),
      finalize(() => this.loadArticles())
    ).subscribe(
      (bookmarks: BookmarkedArticle[]) => {
        this.bookmarkedArticleIds = new Set(bookmarks.map(b => b.article_id));
      }
    );
  }

  loadArticles(): void {
    if (!this.hasMoreArticles) return;

    // Load articles based on the selected category if specified, otherwise load all articles
    this.dashboardService.getArticles(this.selectedCategory, this.currentPage).pipe(
      finalize(() => this.isLoading = false)
    ).subscribe(
      (response) => {
        const articles = response.results.filter(article => !this.bookmarkedArticleIds.has(article.id));
        this.totalPages = Math.ceil(response.count / this.pageSize);

        if (articles.length > 0) {
          this.displayedArticles = articles;
          this.allArticlesBookmarked = false;
        } else {
          this.displayedArticles = [];
          this.allArticlesBookmarked = true;
        }
      },
      (error) => {
        console.error('Error fetching articles:', error);
      }
    );
  }

  checkAdjacentPages(): void {
    if (this.currentPage < this.totalPages) {
      this.dashboardService.getArticles(this.selectedCategory, this.currentPage + 1).subscribe(
        (response) => {
          this.hasMoreArticles = response.results.length > 0;
          if (!this.hasMoreArticles && this.currentPage > 1) {
            this.currentPage--;
            this.loadArticles(); // Load previous page if no more articles on the next page
          }
        },
        (error) => {
          console.error('Error checking adjacent pages:', error);
        }
      );
    } else if (this.currentPage > 1) {
      this.currentPage--;
      this.loadArticles(); // Load previous page if current page is last and all articles are bookmarked
    } else {
      this.allArticlesBookmarked = true;
      this.displayedArticles = []; // Ensure no articles are displayed on the first page if all are bookmarked
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadArticles();
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadArticles();
    }
  }

  toggleBookmark(article: Article): void {
    if (!this.bookmarkedArticleIds.has(article.id)) {
      this.bookmarkService.addBookmark(article.id).pipe(
        catchError(error => {
          console.error('Error adding bookmark:', error);
          return of(null);
        })
      ).subscribe(
        (response) => {
          this.bookmarkedArticleIds.add(article.id);
          this.displayedArticles = this.displayedArticles.filter(a => a.id !== article.id);

          if (this.displayedArticles.length === 0) {
            this.allArticlesBookmarked = true;
            this.checkAdjacentPages();
          }
          
          this.showBookmarkMessage = true;
          this.bookmarkMessage = response.message || 'Bookmark saved successfully';
          this.hideMessageAfterDelay();
        }
      );
    }
  }

  hideMessageAfterDelay(): void {
    setTimeout(() => {
      this.showBookmarkMessage = false;
    }, 500);
  }

  isBookmarked(articleId: number): boolean {
    return this.bookmarkedArticleIds.has(articleId);
  }

  viewArticle(article: Article): void {
    this.router.navigate(['/article', article.id]);
  }

  navigateToBookmarks(): void {
    this.router.navigate(['/bookmarks']);
  }

  onCategoryChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.selectedCategory = target.value;
    this.currentPage = 1;
    this.isLoading = true;

    this.dashboardService.setSelectedCategory(this.selectedCategory);

    this.router.navigate([], {
      queryParams: { category: this.selectedCategory },
      queryParamsHandling: 'merge'
    });

    this.loadBookmarksAndArticles();
  }
}
