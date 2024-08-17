import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../dashboard.service';

interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
  article_id?: number;
}

@Component({
  selector: 'app-notification',
  templateUrl: './notification.component.html',
  styleUrls: ['./notification.component.css']
})
export class NotificationComponent implements OnInit {
  notifications: Notification[] = [];

  constructor(private dashboardService: DashboardService) { }

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.dashboardService.getNotifications().subscribe(
      (data) => {
        this.notifications = data;
      },
      (error) => {
        console.error('Error fetching notifications:', error);
      }
    );
  }

  deleteNotification(notificationId: number): void {
    this.dashboardService.deleteNotification(notificationId).subscribe(
      () => {
        this.notifications = this.notifications.filter(n => n.id !== notificationId);
      },
      (error) => {
        console.error('Error deleting notification:', error);
      }
    );
  }
}