import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AuthInterceptor } from './auth.interceptor';
import { AuthService } from './auth.service';
import { DashboardService } from './dashboard.service';
import { ArticlesComponent } from './articles/articles.component';
import { BookmarksComponent } from './bookmarks/bookmarks.component';
import { NavbarComponent } from './navbar/navbar.component';
import { ArticleDetailComponent } from './article-detail/article-detail.component';
import { WeatherComponent } from './weather/weather.component';
import { NotificationComponent } from './notification/notification.component';


@NgModule({
  declarations: [
    AppComponent,
    RegisterComponent,
    LoginComponent,
    DashboardComponent,
    ArticlesComponent,
    BookmarksComponent,
    NavbarComponent,
    ArticleDetailComponent,
    WeatherComponent,
    NotificationComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule, // Added ReactiveFormsModule
    HttpClientModule
  ],
  providers: [
    AuthService,
    DashboardService,
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
