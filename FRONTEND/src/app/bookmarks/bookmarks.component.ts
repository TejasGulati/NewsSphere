import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { BookmarkService } from '../bookmark.service';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';

interface BookmarkedArticle {
  id: number;
  article_title: string;
  article_url: string;
  article_id: number;
  article_content: string;
  article_media_url: string;
  created_at: string;
  user: number;
}

@Component({
  selector: 'app-bookmarks',
  templateUrl: './bookmarks.component.html',
  styleUrls: ['./bookmarks.component.css']
})
export class BookmarksComponent implements OnInit {
  bookmarkedArticles: BookmarkedArticle[] = [];
  showBookmarkMessage: boolean = false;
  bookmarkMessage: string = '';

  constructor(
    private bookmarkService: BookmarkService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadBookmarks();
  }

  loadBookmarks(): void {
    this.bookmarkService.getBookmarks().subscribe(
      bookmarks => {
        this.bookmarkedArticles = bookmarks;
      },
      error => {
        console.error('Error loading bookmarks:', error);
      }
    );
  }

  removeBookmark(bookmarkedArticle: BookmarkedArticle): void {
    if (bookmarkedArticle && bookmarkedArticle.article_id) {
      // Remove the bookmark from the local list immediately
      this.bookmarkedArticles = this.bookmarkedArticles.filter(a => a.id !== bookmarkedArticle.id);

      // Then make the API call to remove it from the server
      this.bookmarkService.removeBookmark(bookmarkedArticle.article_id).pipe(
        catchError(error => {
          console.error('Error removing bookmark:', error);
          // If there's an error, add the bookmark back to the list
          this.bookmarkedArticles.push(bookmarkedArticle);
          this.showBookmarkMessage = true;
          this.bookmarkMessage = 'Error removing bookmark';
          this.hideMessageAfterDelay();
          return of(null);
        })
      ).subscribe(
        () => {
          // Bookmark successfully removed from the server
          this.showBookmarkMessage = true;
          this.bookmarkMessage = 'Bookmark removed successfully';
          this.hideMessageAfterDelay();
        }
      );
    } else {
      console.error('Invalid bookmark or article ID', bookmarkedArticle);
    }
  }

  viewArticle(articleId: number): void {
    this.router.navigate(['/article', articleId]);
  }

  hideMessageAfterDelay(): void {
    setTimeout(() => {
      this.showBookmarkMessage = false;
    }, 500);
  }
}
