import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ArticlesComponent } from './articles/articles.component';
import { BookmarksComponent } from './bookmarks/bookmarks.component';
import { authGuard } from './auth.guard';
import { ArticleDetailComponent } from './article-detail/article-detail.component';
import { WeatherComponent } from './weather/weather.component'; // Import WeatherComponent

const routes: Routes = [
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [authGuard] },
  { path: 'articles', component: ArticlesComponent, canActivate: [authGuard] },
  { path: 'article/:id', component: ArticleDetailComponent, canActivate: [authGuard] },
  { path: 'bookmarks', component: BookmarksComponent, canActivate: [authGuard] },
  { path: 'weather', component: WeatherComponent, canActivate: [authGuard] }, // Add Weather route
  { path: '', redirectTo: '', pathMatch: 'full' }, // Default redirect to dashboard
  { path: '**', redirectTo: '' } // Wildcard route for any undefined paths
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
