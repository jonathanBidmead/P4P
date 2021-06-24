r = 2;
theta1 = 30;
theta2 = 60;
theta3 = 30;
theta4 = 40;

x1 = r*cosd(theta1);
y1 = r*sind(theta1);
z1 = r*sind(theta3);

x2 = x1+r*cosd(theta1);
y2 = y1+r*sind(theta2);
z2 = z1+r*sind(theta4);
hold on
view(3)
axis([-1 5 -1 5 -1 5])
plot3([0 x1 x2], [0 y1 y2], [0 z1 z2]);