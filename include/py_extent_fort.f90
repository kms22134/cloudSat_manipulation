module extent_interface
use iso_c_binding, only: c_double, c_int
use extent_module, only: gfunc
implicit none
contains
subroutine c_gfunc() bind(c)
    integer(c_int) :: x

    x = 10
    !call gfunc()
end subroutine
end module
