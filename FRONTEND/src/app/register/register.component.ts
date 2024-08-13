import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;
  errorMessage: string = '';
  successMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      name: ['', [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(50),
        this.noWhitespaceValidator,
        this.lettersAndSpacesOnlyValidator
      ]],
      email: ['', [
        Validators.required,
        Validators.email,
        Validators.maxLength(100),
        this.noWhitespaceValidator,
        this.forbiddenDomainValidator(['example.com', 'test.com']),
        this.customEmailPatternValidator
      ]],
      password: ['', [
        Validators.required,
        Validators.minLength(8),
        Validators.maxLength(100),
        Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).+$/),
        this.noWhitespaceValidator,
        this.minSpecialCharactersValidator(2)
      ]]
    });
  }

  ngOnInit(): void {}

  onRegister(): void {
    if (this.registerForm.valid) {
      const { name, email, password } = this.registerForm.value;
      this.authService.register(name, email, password).subscribe({
        next: () => {
          this.successMessage = 'Registration successful. Redirecting to login...';
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 4000);
        },
        error: (error: any) => {
          console.error('Registration error:', error);
          this.errorMessage = this.getServerErrorMessage(error);
          setTimeout(() => {
            this.errorMessage = ''; // Clear the error message after 3 seconds
          }, 4000);
        }
      });
    } else {
      this.errorMessage = this.getFormErrors(this.registerForm);
      setTimeout(() => {
        this.errorMessage = ''; // Clear the error message after 3 seconds
      }, 4000);
    }
  }

  // Custom validator to check for whitespace
  private noWhitespaceValidator(control: AbstractControl): ValidationErrors | null {
    const isWhitespace = (control.value || '').trim().length === 0;
    return isWhitespace ? { 'noWhitespace': 'The field cannot contain only whitespace.' } : null;
  }

  // Custom validator to disallow certain domains
  private forbiddenDomainValidator(forbiddenDomains: string[]) {
    return (control: AbstractControl): ValidationErrors | null => {
      const emailDomain = control.value?.split('@')[1];
      return forbiddenDomains.includes(emailDomain) ? { 'forbiddenDomain': `Email addresses from the domain '${emailDomain}' are not allowed.` } : null;
    };
  }

  // Custom validator for additional email pattern checks
  private customEmailPatternValidator(control: AbstractControl): ValidationErrors | null {
    const forbiddenPatterns = [
      { pattern: /.+@.+\.\d+/, message: 'Email addresses ending with numbers (e.g., user@domain.123) are not allowed.' },
      { pattern: /^[^@]*$/, message: 'Email address must contain an "@" symbol.' },
      { pattern: /@[^.]*$/, message: 'Email address must contain a domain extension (e.g., .com, .org).' },
      { pattern: /^.*@.*\.\..*$/, message: 'Email addresses with double dots after the domain (e.g., user@domain..com) are not allowed.' }
    ];

    for (const rule of forbiddenPatterns) {
      if (rule.pattern.test(control.value)) {
        return { 'invalidEmailPattern': rule.message };
      }
    }
    return null;
  }

  // Custom validator for name to only allow letters and spaces
  private lettersAndSpacesOnlyValidator(control: AbstractControl): ValidationErrors | null {
    const namePattern = /^[A-Za-z\s]+$/;
    return namePattern.test(control.value) ? null : { 'lettersAndSpacesOnly': 'Name can only contain letters and spaces.' };
  }

  // Custom validator for password to ensure minimum special characters
  private minSpecialCharactersValidator(minSpecialChars: number) {
    return (control: AbstractControl): ValidationErrors | null => {
      const value = control.value || '';
      const specialCharsCount = (value.match(/[\W_]/g) || []).length;
      return specialCharsCount >= minSpecialChars ? null : { 'minSpecialCharacters': `Password must contain at least ${minSpecialChars} special characters.` };
    };
  }

  // Extract detailed error messages
  private getFormErrors(form: FormGroup): string {
    const errorMessages: string[] = [];

    Object.keys(form.controls).forEach(controlName => {
      const control = form.get(controlName);
      if (control && control.errors) {
        Object.keys(control.errors).forEach(errorKey => {
          let errorMessage = '';
          if (control.errors && control.errors[errorKey]) { // Ensure control.errors and control.errors[errorKey] are not null
            switch (errorKey) {
              case 'required':
                errorMessage = `${this.capitalizeFirstLetter(controlName)} is required.`;
                break;
              case 'minlength':
                errorMessage = `${this.capitalizeFirstLetter(controlName)} must be at least ${control.errors[errorKey].requiredLength} characters long.`;
                break;
              case 'maxlength':
                errorMessage = `${this.capitalizeFirstLetter(controlName)} cannot be more than ${control.errors[errorKey].requiredLength} characters long.`;
                break;
              case 'email':
                errorMessage = `Please enter a valid email address for ${this.capitalizeFirstLetter(controlName)}.`;
                break;
              case 'noWhitespace':
                errorMessage = `No whitespace allowed in ${this.capitalizeFirstLetter(controlName)}.`;
                break;
              case 'forbiddenDomain':
                errorMessage = `Email addresses from the domain '${control.errors[errorKey]}' are not allowed.`;
                break;
              case 'invalidEmailPattern':
                errorMessage = control.errors[errorKey];
                break;
              case 'lettersAndSpacesOnly':
                errorMessage = `Name can only contain letters and spaces.`;
                break;
              case 'minSpecialCharacters':
                errorMessage = control.errors[errorKey];
                break;
              default:
                errorMessage = `Invalid value for ${this.capitalizeFirstLetter(controlName)}.`;
                break;
            }
            errorMessages.push(errorMessage);
          }
        });
      }
    });

    return errorMessages.join(' ');
  }

  // Capitalize the first letter of a string
  private capitalizeFirstLetter(string: string): string {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  // Generate server error messages
  private getServerErrorMessage(error: any): string {
    if (error.status === 400) {
      // Handle specific 400 error cases
      return this.handleBadRequestError(error);
    } else if (error.status === 401) {
      return 'Unauthorized access. Please check your credentials.';
    } else if (error.status === 403) {
      return 'Forbidden access. You do not have permission to perform this action.';
    } else if (error.status === 404) {
      return 'The requested resource was not found.';
    } else if (error.status === 500) {
      return 'Server error. Please try again later.';
    } else {
      return 'An unexpected error occurred. Please try again.';
    }
  }

  // Handle specific 400 Bad Request errors
  private handleBadRequestError(error: any): string {
    if (error.error.email === 'Email already in use') {
      return 'This email is already in use. Please use a different email address.';
    } else if (error.error.email === 'Invalid email address') {
      return 'Invalid email address. Please check your input.';
    } else if (error.error.password === 'Weak password') {
      return 'Password is too weak. Ensure it meets all security requirements.';
    } else {
      return 'Invalid registration details. Please check your input.';
    }
  }
}
