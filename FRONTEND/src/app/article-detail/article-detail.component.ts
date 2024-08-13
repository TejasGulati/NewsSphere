import { Component, OnInit, HostListener } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DashboardService } from '../dashboard.service';

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

@Component({
  selector: 'app-article-detail',
  templateUrl: './article-detail.component.html',
  styleUrls: ['./article-detail.component.css']
})
export class ArticleDetailComponent implements OnInit {
  article: Article | undefined;
  isDropdownOpen: boolean = false;
  isModalOpen: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private dashboardService: DashboardService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const articleId = +params.get('id')!;
      this.dashboardService.getArticle(articleId).subscribe(
        article => this.article = article,
        error => console.error('Error fetching article:', error)
      );
    });
  }

  exploreOtherArticles(): void {
    this.router.navigate(['/articles']);
  }

  shareOnWhatsApp(): void {
    if (this.article?.source_url) {
      const phoneNumber = '1XXXXXXXXXX'; // Replace with your phone number
      const message = `Check out this article: ${this.article.source_url}`;
      const url = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;
      window.open(url, '_blank');
    } else {
      console.warn('No source URL available for WhatsApp sharing.');
    }
  }

  copyToClipboard(): void {
    if (this.article?.source_url) {
      const message = `Check out this article: ${this.article.source_url}`;
      navigator.clipboard.writeText(message).then(() => {
        alert('Article link copied to clipboard! You can now paste it into Instagram.');
      }).catch(err => {
        console.error('Failed to copy: ', err);
      });
    } else {
      console.warn('No source URL available to copy.');
    }
  }

  shareOnFacebook(): void {
    if (this.article?.source_url) {
      const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(this.article.source_url)}`;
      window.open(url, '_blank', 'width=600,height=400');
    } else {
      console.warn('No source URL available for Facebook sharing.');
    }
  }

  toggleDropdown(): void {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  closeModal(): void {
    this.isModalOpen = false;
  }

  toggleModal(): void {
    this.isModalOpen = !this.isModalOpen;
  }

  openSource(): void {
    if (this.article?.source_url) {
      window.open(this.article.source_url, '_blank');
    } else {
      console.warn('No source URL available to open.');
    }
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    const targetElement = event.target as HTMLElement;
    const clickedInside = targetElement.closest('.share-dropdown-container') !== null;

    if (!clickedInside && this.isDropdownOpen) {
      this.isDropdownOpen = false;
    }
  }
}
